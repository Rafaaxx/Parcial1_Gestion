"""Integration tests for Pedido FSM (State Machine).

CRITICAL: These tests require PostgreSQL because they use SELECT FOR UPDATE
for stock operations. SQLite does NOT support SELECT FOR UPDATE.

All tests in this module are marked with @pytest.mark.postgres and will
be skipped if PostgreSQL is not available.
"""

from decimal import Decimal

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel

# Mark all tests in this module to require PostgreSQL
pytestmark = pytest.mark.postgres


# ── Test data helpers ────────────────────────────────────────────────────────────


async def _create_test_user_with_roles(session: AsyncSession, email: str, roles: list[str]) -> dict:
    """Create a test user with specified roles."""
    from passlib.context import CryptContext

    from app.models.rol import Rol
    from app.models.usuario import Usuario
    from app.models.usuario_rol import UsuarioRol

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    usuario = Usuario(
        email=email,
        password_hash=pwd_context.hash("Test1234!"),
        nombre="Test",
        apellido="User",
        activo=True,
    )
    session.add(usuario)
    await session.flush()
    await session.refresh(usuario)

    # Assign roles
    for role_codigo in roles:
        rol_result = await session.execute(select(Rol).where(Rol.codigo == role_codigo))
        rol = rol_result.scalar_one_or_none()
        if rol:
            usuario_rol = UsuarioRol(
                usuario_id=usuario.id,
                rol_codigo=rol.codigo,
                asignado_por_id=usuario.id,
            )
            session.add(usuario_rol)

    await session.flush()

    return {"id": usuario.id, "email": email, "roles": roles}


async def _create_test_producto(
    session: AsyncSession,
    nombre: str = "Test Pizza",
    precio: Decimal = Decimal("100.00"),
    stock: int = 50,
) -> dict:
    """Create a test product."""
    from app.models.producto import Producto

    producto = Producto(
        nombre=nombre,
        descripcion="Delicious test product",
        precio_base=precio,
        stock_cantidad=stock,
        disponible=True,
    )
    session.add(producto)
    await session.flush()
    await session.refresh(producto)

    return {
        "id": producto.id,
        "nombre": producto.nombre,
        "precio": producto.precio_base,
        "stock": producto.stock_cantidad,
    }


async def _create_test_pedido(
    session: AsyncSession, usuario_id: int, estado: str = "PENDIENTE"
) -> dict:
    """Create a test order."""
    from app.models.pedido import Pedido

    pedido = Pedido(
        usuario_id=usuario_id,
        estado_codigo=estado,
        total=Decimal("150.00"),
        costo_envio=Decimal("50.00"),
        forma_pago_codigo="EFECTIVO",
    )
    session.add(pedido)
    await session.flush()
    await session.refresh(pedido)

    return {"id": pedido.id, "estado": pedido.estado_codigo}


async def _add_detalle_pedido(
    session: AsyncSession, pedido_id: int, producto_id: int, cantidad: int = 1
) -> dict:
    """Add a detail to an order."""
    from app.models.pedido import DetallePedido
    from app.models.producto import Producto

    # Get product for snapshot
    producto = await session.get(Producto, producto_id)

    detalle = DetallePedido(
        pedido_id=pedido_id,
        producto_id=producto_id,
        nombre_snapshot=producto.nombre,
        precio_snapshot=producto.precio_base,
        cantidad=cantidad,
    )
    session.add(detalle)
    await session.flush()
    await session.refresh(detalle)

    return {"id": detalle.id, "cantidad": detalle.cantidad}


async def _get_stock_producto(session: AsyncSession, producto_id: int) -> int:
    """Get current stock of a product."""
    from app.models.producto import Producto

    producto = await session.get(Producto, producto_id)
    return producto.stock_cantidad if producto else 0


# ── Test: FSM Map Validation ───────────────────────────────────────────────────


class TestFSMMapValidation:
    """Test that the FSM transition map is correctly defined."""

    def test_all_states_have_entries(self):
        """Verify all 6 states are in the FSM map."""
        from app.modules.pedidos.fsm import FSM_TRANSITION_MAP, EstadoPedido

        expected_states = {e.value for e in EstadoPedido}
        actual_states = set(FSM_TRANSITION_MAP.keys())

        assert (
            expected_states == actual_states
        ), f"Missing states: {expected_states - actual_states}"

    def test_forward_transitions_defined(self):
        """Verify forward transitions are in the map."""
        from app.modules.pedidos.fsm import FSM_TRANSITION_MAP

        # PENDIENTE -> CONFIRMADO
        pend_conf = [t for t in FSM_TRANSITION_MAP["PENDIENTE"] if t.target == "CONFIRMADO"]
        assert len(pend_conf) == 1, "PENDIENTE->CONFIRMADO transition missing"

        # CONFIRMADO -> EN_PREP
        conf_enprep = [t for t in FSM_TRANSITION_MAP["CONFIRMADO"] if t.target == "EN_PREP"]
        assert len(conf_enprep) == 1, "CONFIRMADO->EN_PREP transition missing"

        # EN_PREP -> EN_CAMINO
        enprep_encamino = [t for t in FSM_TRANSITION_MAP["EN_PREP"] if t.target == "EN_CAMINO"]
        assert len(enprep_encamino) == 1, "EN_PREP->EN_CAMINO transition missing"

        # EN_CAMINO -> ENTREGADO
        encamino_entregado = [t for t in FSM_TRANSITION_MAP["EN_CAMINO"] if t.target == "ENTREGADO"]
        assert len(encamino_entregado) == 1, "EN_CAMINO->ENTREGADO transition missing"

    def test_cancel_transitions_defined(self):
        """Verify cancel transitions from non-terminal states."""
        from app.modules.pedidos.fsm import FSM_TRANSITION_MAP

        # PENDIENTE -> CANCELADO
        pend_cancel = [t for t in FSM_TRANSITION_MAP["PENDIENTE"] if t.target == "CANCELADO"]
        assert len(pend_cancel) == 1, "PENDIENTE->CANCELADO transition missing"

        # CONFIRMADO -> CANCELADO
        conf_cancel = [t for t in FSM_TRANSITION_MAP["CONFIRMADO"] if t.target == "CANCELADO"]
        assert len(conf_cancel) == 1, "CONFIRMADO->CANCELADO transition missing"

        # EN_PREP -> CANCELADO
        enprep_cancel = [t for t in FSM_TRANSITION_MAP["EN_PREP"] if t.target == "CANCELADO"]
        assert len(enprep_cancel) == 1, "EN_PREP->CANCELADO transition missing"

    def test_terminal_states_have_no_transitions(self):
        """Verify terminal states have empty transition lists."""
        from app.modules.pedidos.fsm import FSM_TRANSITION_MAP

        assert FSM_TRANSITION_MAP["ENTREGADO"] == [], "ENTREGADO should have no transitions"
        assert FSM_TRANSITION_MAP["CANCELADO"] == [], "CANCELADO should have no transitions"

    def test_terminal_detection(self):
        """Verify es_estado_terminal correctly identifies terminal states."""
        from app.modules.pedidos.fsm import es_estado_terminal

        assert es_estado_terminal("ENTREGADO") is True
        assert es_estado_terminal("CANCELADO") is True
        assert es_estado_terminal("PENDIENTE") is False
        assert es_estado_terminal("CONFIRMADO") is False
        assert es_estado_terminal("EN_PREP") is False
        assert es_estado_terminal("EN_CAMINO") is False


# ── Test: Valid Transitions via API ──────────────────────────────────────────


class TestValidTransitions:
    """Test valid state transitions through the API."""

    @pytest.mark.asyncio
    async def test_pendiente_to_confirmado_by_admin(
        self, pg_client: AsyncClient, pg_session: AsyncSession
    ):
        """Test PENDIENTE -> CONFIRMADO transition by ADMIN."""
        from app.security import create_access_token

        # Setup: create user, product, order
        admin = await _create_test_user_with_roles(pg_session, "admin@test.com", ["ADMIN"])
        producto = await _create_test_producto(pg_session, "Pizza Test", Decimal("100.00"), 50)
        pedido = await _create_test_pedido(pg_session, admin["id"], "PENDIENTE")
        await _add_detalle_pedido(pg_session, pedido["id"], producto["id"], 2)
        await pg_session.commit()

        # Generate token for admin
        token = create_access_token(
            {"sub": str(admin["id"]), "email": admin["email"], "roles": ["ADMIN"]}
        )

        # Execute transition
        response = await pg_client.patch(
            f"/api/v1/pedidos/{pedido['id']}/estado",
            json={"nuevo_estado": "CONFIRMADO"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert (
            response.status_code == 200
        ), f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data["estado_codigo"] == "CONFIRMADO"

    @pytest.mark.asyncio
    async def test_confirmado_to_en_prep_by_admin(
        self, pg_client: AsyncClient, pg_session: AsyncSession
    ):
        """Test CONFIRMADO -> EN_PREP transition."""
        from app.security import create_access_token

        admin = await _create_test_user_with_roles(pg_session, "admin@test.com", ["ADMIN"])
        producto = await _create_test_producto(pg_session, "Pizza Test", Decimal("100.00"), 50)
        pedido = await _create_test_pedido(pg_session, admin["id"], "CONFIRMADO")
        await _add_detalle_pedido(pg_session, pedido["id"], producto["id"], 1)
        await pg_session.commit()

        # Generate token for admin
        token = create_access_token(
            {"sub": str(admin["id"]), "email": admin["email"], "roles": ["ADMIN"]}
        )

        response = await pg_client.patch(
            f"/api/v1/pedidos/{pedido['id']}/estado",
            json={"nuevo_estado": "EN_PREP"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert (
            response.status_code == 200
        ), f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data["estado_codigo"] == "EN_PREP"

    @pytest.mark.asyncio
    async def test_en_prep_to_en_camino_by_admin(
        self, pg_client: AsyncClient, pg_session: AsyncSession
    ):
        """Test EN_PREP -> EN_CAMINO transition."""
        from app.security import create_access_token

        admin = await _create_test_user_with_roles(pg_session, "admin@test.com", ["ADMIN"])
        producto = await _create_test_producto(pg_session, "Pizza Test", Decimal("100.00"), 50)
        pedido = await _create_test_pedido(pg_session, admin["id"], "EN_PREP")
        await _add_detalle_pedido(pg_session, pedido["id"], producto["id"], 1)
        await pg_session.commit()

        # Generate token for admin
        token = create_access_token(
            {"sub": str(admin["id"]), "email": admin["email"], "roles": ["ADMIN"]}
        )

        response = await pg_client.patch(
            f"/api/v1/pedidos/{pedido['id']}/estado",
            json={"nuevo_estado": "EN_CAMINO"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert (
            response.status_code == 200
        ), f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data["estado_codigo"] == "EN_CAMINO"

    @pytest.mark.asyncio
    async def test_en_camino_to_entregado_by_admin(
        self, pg_client: AsyncClient, pg_session: AsyncSession
    ):
        """Test EN_CAMINO -> ENTREGADO transition."""
        from app.security import create_access_token

        admin = await _create_test_user_with_roles(pg_session, "admin@test.com", ["ADMIN"])
        producto = await _create_test_producto(pg_session, "Pizza Test", Decimal("100.00"), 50)
        pedido = await _create_test_pedido(pg_session, admin["id"], "EN_CAMINO")
        await _add_detalle_pedido(pg_session, pedido["id"], producto["id"], 1)
        await pg_session.commit()

        # Generate token for admin
        token = create_access_token(
            {"sub": str(admin["id"]), "email": admin["email"], "roles": ["ADMIN"]}
        )

        response = await pg_client.patch(
            f"/api/v1/pedidos/{pedido['id']}/estado",
            json={"nuevo_estado": "ENTREGADO"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert (
            response.status_code == 200
        ), f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data["estado_codigo"] == "ENTREGADO"


# ── Test: Invalid Transitions Rejected ───────────────────────────────────────


class TestInvalidTransitions:
    """Test that invalid transitions are properly rejected."""

    @pytest.mark.asyncio
    async def test_pendiente_to_en_camino_rejected(
        self, pg_client: AsyncClient, pg_session: AsyncSession
    ):
        """Test PENDIENTE -> EN_CAMINO is invalid (skipping CONFIRMADO and EN_PREP)."""
        from app.security import create_access_token

        admin = await _create_test_user_with_roles(pg_session, "admin@test.com", ["ADMIN"])
        producto = await _create_test_producto(pg_session, "Pizza Test", Decimal("100.00"), 50)
        pedido = await _create_test_pedido(pg_session, admin["id"], "PENDIENTE")
        await _add_detalle_pedido(pg_session, pedido["id"], producto["id"], 1)
        await pg_session.commit()

        token = create_access_token(
            {"sub": str(admin["id"]), "email": admin["email"], "roles": ["ADMIN"]}
        )

        response = await pg_client.patch(
            f"/api/v1/pedidos/{pedido['id']}/estado",
            json={"nuevo_estado": "EN_CAMINO"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 422, f"Expected 422, got {response.status_code}"
        assert "Transición no válida" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_confirmado_to_entregado_rejected(
        self, pg_client: AsyncClient, pg_session: AsyncSession
    ):
        """Test CONFIRMADO -> ENTREGADO is invalid (skipping EN_PREP and EN_CAMINO)."""
        from app.security import create_access_token

        admin = await _create_test_user_with_roles(pg_session, "admin@test.com", ["ADMIN"])
        producto = await _create_test_producto(pg_session, "Pizza Test", Decimal("100.00"), 50)
        pedido = await _create_test_pedido(pg_session, admin["id"], "CONFIRMADO")
        await _add_detalle_pedido(pg_session, pedido["id"], producto["id"], 1)
        await pg_session.commit()

        token = create_access_token(
            {"sub": str(admin["id"]), "email": admin["email"], "roles": ["ADMIN"]}
        )

        response = await pg_client.patch(
            f"/api/v1/pedidos/{pedido['id']}/estado",
            json={"nuevo_estado": "ENTREGADO"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 422
        assert "Transición no válida" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_backward_transition_rejected(
        self, pg_client: AsyncClient, pg_session: AsyncSession
    ):
        """Test backward transition (EN_CAMINO -> EN_PREP) is invalid."""
        from app.security import create_access_token

        admin = await _create_test_user_with_roles(pg_session, "admin@test.com", ["ADMIN"])
        producto = await _create_test_producto(pg_session, "Pizza Test", Decimal("100.00"), 50)
        pedido = await _create_test_pedido(pg_session, admin["id"], "EN_CAMINO")
        await _add_detalle_pedido(pg_session, pedido["id"], producto["id"], 1)
        await pg_session.commit()

        token = create_access_token(
            {"sub": str(admin["id"]), "email": admin["email"], "roles": ["ADMIN"]}
        )

        response = await pg_client.patch(
            f"/api/v1/pedidos/{pedido['id']}/estado",
            json={"nuevo_estado": "EN_PREP"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 422
        assert "Transición no válida" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_pedidos_role_cannot_cancel_confirmado(
        self, pg_client: AsyncClient, pg_session: AsyncSession
    ):
        """Test PEDIDOS role cannot cancel CONFIRMADO orders (only ADMIN can)."""
        pedidos_user = await _create_test_user_with_roles(
            pg_session, "pedidos@test.com", ["PEDIDOS"]
        )
        producto = await _create_test_producto(pg_session, "Pizza Test", Decimal("100.00"), 50)
        pedido = await _create_test_pedido(pg_session, pedidos_user["id"], "CONFIRMADO")
        await _add_detalle_pedido(pg_session, pedido["id"], producto["id"], 1)
        await pg_session.commit()

        # Login as PEDIDOS
        from app.security import create_access_token

        token = create_access_token(
            {"sub": str(pedidos_user["id"]), "email": pedidos_user["email"], "roles": ["PEDIDOS"]}
        )

        response = await pg_client.patch(
            f"/api/v1/pedidos/{pedido['id']}/estado",
            json={"nuevo_estado": "CANCELADO", "motivo": "Test cancel"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 422, f"PEDIDOS should not be able to cancel CONFIRMADO"
        # The FSM map shows CONFIRMADO -> CANCELADO only for ADMIN, not PEDIDOS


# ── Test: Terminal State Rejection ───────────────────────────────────────────


class TestTerminalStateRejection:
    """Test that terminal states cannot transition."""

    @pytest.mark.asyncio
    async def test_entregado_cannot_transition(
        self, pg_client: AsyncClient, pg_session: AsyncSession
    ):
        """Test ENTREGADO (terminal) rejects any transition."""
        from app.security import create_access_token

        admin = await _create_test_user_with_roles(pg_session, "admin@test.com", ["ADMIN"])
        producto = await _create_test_producto(pg_session, "Pizza Test", Decimal("100.00"), 50)
        pedido = await _create_test_pedido(pg_session, admin["id"], "ENTREGADO")
        await _add_detalle_pedido(pg_session, pedido["id"], producto["id"], 1)
        await pg_session.commit()

        token = create_access_token(
            {"sub": str(admin["id"]), "email": admin["email"], "roles": ["ADMIN"]}
        )

        response = await pg_client.patch(
            f"/api/v1/pedidos/{pedido['id']}/estado",
            json={"nuevo_estado": "CANCELADO"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 422
        assert "terminal" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_cancelado_cannot_transition(
        self, pg_client: AsyncClient, pg_session: AsyncSession
    ):
        """Test CANCELADO (terminal) rejects any transition."""
        from app.security import create_access_token

        admin = await _create_test_user_with_roles(pg_session, "admin@test.com", ["ADMIN"])
        producto = await _create_test_producto(pg_session, "Pizza Test", Decimal("100.00"), 50)
        pedido = await _create_test_pedido(pg_session, admin["id"], "CANCELADO")
        await _add_detalle_pedido(pg_session, pedido["id"], producto["id"], 1)
        await pg_session.commit()

        token = create_access_token(
            {"sub": str(admin["id"]), "email": admin["email"], "roles": ["ADMIN"]}
        )

        response = await pg_client.patch(
            f"/api/v1/pedidos/{pedido['id']}/estado",
            json={"nuevo_estado": "CONFIRMADO"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 422
        assert "terminal" in response.json()["detail"].lower()


# ── Test: Role-Based Permissions ─────────────────────────────────────────────


class TestRoleBasedPermissions:
    """Test that role permissions are enforced."""

    @pytest.mark.asyncio
    async def test_client_can_cancel_own_pendiente(
        self, pg_client: AsyncClient, pg_session: AsyncSession
    ):
        """Test CLIENT can cancel their own PENDIENTE order."""
        client = await _create_test_user_with_roles(pg_session, "client@test.com", ["CLIENT"])
        producto = await _create_test_producto(pg_session, "Pizza Test", Decimal("100.00"), 50)
        pedido = await _create_test_pedido(pg_session, client["id"], "PENDIENTE")
        await _add_detalle_pedido(pg_session, pedido["id"], producto["id"], 1)
        await pg_session.commit()

        from app.security import create_access_token

        token = create_access_token(
            {"sub": str(client["id"]), "email": client["email"], "roles": ["CLIENT"]}
        )

        response = await pg_client.delete(
            f"/api/v1/pedidos/{pedido['id']}?motivo=Client%20cancels",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert (
            response.status_code == 200
        ), f"CLIENT should be able to cancel own PENDIENTE: {response.text}"
        data = response.json()
        assert data["estado_codigo"] == "CANCELADO"

    @pytest.mark.asyncio
    async def test_client_cannot_cancel_others_pendiente(
        self, pg_client: AsyncClient, pg_session: AsyncSession
    ):
        """Test CLIENT cannot cancel another user's PENDIENTE order."""
        client = await _create_test_user_with_roles(pg_session, "client@test.com", ["CLIENT"])
        other_client = await _create_test_user_with_roles(pg_session, "other@test.com", ["CLIENT"])
        producto = await _create_test_producto(pg_session, "Pizza Test", Decimal("100.00"), 50)
        pedido = await _create_test_pedido(pg_session, other_client["id"], "PENDIENTE")
        await _add_detalle_pedido(pg_session, pedido["id"], producto["id"], 1)
        await pg_session.commit()

        from app.security import create_access_token

        token = create_access_token(
            {"sub": str(client["id"]), "email": client["email"], "roles": ["CLIENT"]}
        )

        response = await pg_client.delete(
            f"/api/v1/pedidos/{pedido['id']}?motivo=Unauthorized%20cancel",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_client_cannot_cancel_confirmado(
        self, pg_client: AsyncClient, pg_session: AsyncSession
    ):
        """Test CLIENT cannot cancel CONFIRMADO orders (only PENDIENTE)."""
        client = await _create_test_user_with_roles(pg_session, "client@test.com", ["CLIENT"])
        producto = await _create_test_producto(pg_session, "Pizza Test", Decimal("100.00"), 50)
        pedido = await _create_test_pedido(pg_session, client["id"], "CONFIRMADO")
        await _add_detalle_pedido(pg_session, pedido["id"], producto["id"], 1)
        await pg_session.commit()

        from app.security import create_access_token

        token = create_access_token(
            {"sub": str(client["id"]), "email": client["email"], "roles": ["CLIENT"]}
        )

        response = await pg_client.delete(
            f"/api/v1/pedidos/{pedido['id']}?motivo=Client%20tries%20cancel",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 403


# ── Test: Stock Operations ───────────────────────────────────────────────────


class TestStockOperations:
    """Test stock decrement and restore operations."""

    @pytest.mark.asyncio
    async def test_stock_decrements_on_confirmado(
        self, pg_client: AsyncClient, pg_session: AsyncSession
    ):
        """Test stock decrements when order transitions to CONFIRMADO."""
        admin = await _create_test_user_with_roles(pg_session, "admin@test.com", ["ADMIN"])
        producto = await _create_test_producto(pg_session, "Pizza Test", Decimal("100.00"), 50)
        initial_stock = await _get_stock_producto(pg_session, producto["id"])

        pedido = await _create_test_pedido(pg_session, admin["id"], "PENDIENTE")
        await _add_detalle_pedido(pg_session, pedido["id"], producto["id"], 5)  # Order 5 units
        await pg_session.commit()

        from app.security import create_access_token

        token = create_access_token(
            {"sub": str(admin["id"]), "email": admin["email"], "roles": ["ADMIN"]}
        )

        response = await pg_client.patch(
            f"/api/v1/pedidos/{pedido['id']}/estado",
            json={"nuevo_estado": "CONFIRMADO"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200

        # Verify stock was decremented
        await pg_session.refresh(
            await pg_session.get(
                type(pg_session.get(Producto, producto["id"])).__bases__[0], producto["id"]
            )
        )
        final_stock = await _get_stock_producto(pg_session, producto["id"])

        # Re-fetch the producto after commit to get updated value
        from app.models.producto import Producto

        prod = await pg_session.get(Producto, producto["id"])
        assert prod.stock_cantidad == initial_stock - 5

    @pytest.mark.asyncio
    async def test_stock_restores_on_cancel_from_confirmado(
        self, pg_client: AsyncClient, pg_session: AsyncSession
    ):
        """Test stock restores when cancelling from CONFIRMADO."""
        admin = await _create_test_user_with_roles(pg_session, "admin@test.com", ["ADMIN"])
        producto = await _create_test_producto(pg_session, "Pizza Test", Decimal("100.00"), 50)

        pedido = await _create_test_pedido(pg_session, admin["id"], "CONFIRMADO")
        await _add_detalle_pedido(pg_session, pedido["id"], producto["id"], 3)
        await pg_session.commit()

        from app.security import create_access_token

        token = create_access_token(
            {"sub": str(admin["id"]), "email": admin["email"], "roles": ["ADMIN"]}
        )

        # Transition to CANCELADO
        response = await pg_client.patch(
            f"/api/v1/pedidos/{pedido['id']}/estado",
            json={"nuevo_estado": "CANCELADO", "motivo": "Test cancellation"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200

        # Verify stock was restored
        from app.models.producto import Producto

        prod = await pg_session.get(Producto, producto["id"])
        assert prod.stock_cantidad == 50  # Back to original

    @pytest.mark.asyncio
    async def test_stock_not_restored_on_pendiente_cancel(
        self, pg_client: AsyncClient, pg_session: AsyncSession
    ):
        """Test stock is NOT restored when cancelling from PENDIENTE (never decremented)."""
        client = await _create_test_user_with_roles(pg_session, "client@test.com", ["CLIENT"])
        producto = await _create_test_producto(pg_session, "Pizza Test", Decimal("100.00"), 50)

        pedido = await _create_test_pedido(pg_session, client["id"], "PENDIENTE")
        await _add_detalle_pedido(pg_session, pedido["id"], producto["id"], 2)
        await pg_session.commit()

        from app.security import create_access_token

        token = create_access_token(
            {"sub": str(client["id"]), "email": client["email"], "roles": ["CLIENT"]}
        )

        # Cancel from PENDIENTE
        response = await pg_client.delete(
            f"/api/v1/pedidos/{pedido['id']}?motivo=Client%20cancel",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200

        # Verify stock unchanged
        from app.models.producto import Producto

        prod = await pg_session.get(Producto, producto["id"])
        assert prod.stock_cantidad == 50  # Unchanged


# ── Test: Motivo Requirement ─────────────────────────────────────────────────


class TestMotivoRequirement:
    """Test that motivo is required for cancellation."""

    @pytest.mark.asyncio
    async def test_motivo_required_for_cancel(
        self, pg_client: AsyncClient, pg_session: AsyncSession
    ):
        """Test that motivo is required when cancelling."""
        admin = await _create_test_user_with_roles(pg_session, "admin@test.com", ["ADMIN"])
        producto = await _create_test_producto(pg_session, "Pizza Test", Decimal("100.00"), 50)
        pedido = await _create_test_pedido(pg_session, admin["id"], "PENDIENTE")
        await _add_detalle_pedido(pg_session, pedido["id"], producto["id"], 1)
        await pg_session.commit()

        from app.security import create_access_token

        token = create_access_token(
            {"sub": str(admin["id"]), "email": admin["email"], "roles": ["ADMIN"]}
        )

        # Try to cancel without motivo
        response = await pg_client.patch(
            f"/api/v1/pedidos/{pedido['id']}/estado",
            json={"nuevo_estado": "CANCELADO"},  # No motivo!
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 422
        assert "motivo" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_motivo_required_for_delete_cancel(
        self, pg_client: AsyncClient, pg_session: AsyncSession
    ):
        """Test that motivo is required for DELETE cancel endpoint."""
        client = await _create_test_user_with_roles(pg_session, "client@test.com", ["CLIENT"])
        producto = await _create_test_producto(pg_session, "Pizza Test", Decimal("100.00"), 50)
        pedido = await _create_test_pedido(pg_session, client["id"], "PENDIENTE")
        await _add_detalle_pedido(pg_session, pedido["id"], producto["id"], 1)
        await pg_session.commit()

        from app.security import create_access_token

        token = create_access_token(
            {"sub": str(client["id"]), "email": client["email"], "roles": ["CLIENT"]}
        )

        # Try to cancel without motivo
        response = await pg_client.delete(
            f"/api/v1/pedidos/{pedido['id']}",  # No query param!
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 422
        assert "motivo" in response.json()["detail"].lower()
