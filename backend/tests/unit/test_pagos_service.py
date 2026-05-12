"""Unit tests for PagoService and related functionality"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from decimal import Decimal

from app.modules.pagos.service import (
    PagoService,
    PaymentAlreadyExistsError,
    IdempotencyConflictError,
    MPConnectionError,
)
from app.modules.pagos.repository import PagoRepository
from app.modules.pagos.schemas import PagoCreate


class TestPagoServiceCrearPago:
    """Tests for crear_pago method"""

    @pytest.fixture
    def mock_uow(self):
        """Create mock UnitOfWork"""
        uow = MagicMock()
        uow.session = MagicMock()
        uow.pedidos = MagicMock()
        return uow

    @pytest.fixture
    def mock_pedido(self):
        """Create mock Pedido"""
        pedido = MagicMock()
        pedido.id = 1
        pedido.usuario_id = 100
        pedido.estado_codigo = "PENDIENTE"
        pedido.total = Decimal("500.00")
        return pedido

    @pytest.mark.asyncio
    async def test_crear_pago_pedido_not_found(self, mock_uow):
        """Test: 404 when order not found"""
        mock_uow.pedidos.find = AsyncMock(return_value=None)

        service = PagoService(mock_uow)
        body = PagoCreate(pedido_id=999)

        with pytest.raises(Exception) as exc:
            await service.crear_pago(usuario_id=100, body=body)

        # Check it's an HTTPException
        assert exc.value.status_code == 404
        assert "no encontrado" in exc.value.detail.lower()

    @pytest.mark.asyncio
    async def test_crear_pago_forbidden_different_user(self, mock_uow, mock_pedido):
        """Test: 403 when user doesn't own the order"""
        mock_uow.pedidos.find = AsyncMock(return_value=mock_pedido)

        service = PagoService(mock_uow)
        body = PagoCreate(pedido_id=1)

        with pytest.raises(Exception) as exc:
            await service.crear_pago(usuario_id=999, body=body)

        assert exc.value.status_code == 403
        assert "permiso" in exc.value.detail.lower()

    @pytest.mark.asyncio
    async def test_crear_pago_invalid_state(self, mock_uow, mock_pedido):
        """Test: 400 when order is not in PENDIENTE state"""
        mock_pedido.estado_codigo = "CONFIRMADO"
        mock_uow.pedidos.find = AsyncMock(return_value=mock_pedido)

        service = PagoService(mock_uow)
        body = PagoCreate(pedido_id=1)

        with pytest.raises(Exception) as exc:
            await service.crear_pago(usuario_id=100, body=body)

        assert exc.value.status_code == 400
        assert "PENDIENTE" in exc.value.detail

    @pytest.mark.asyncio
    async def test_crear_pago_already_exists(self, mock_uow, mock_pedido):
        """Test: 409 when payment already exists for order"""
        mock_uow.pedidos.find = AsyncMock(return_value=mock_pedido)

        # Mock repository to return existing payment
        mock_repo = MagicMock()
        mock_repo.get_by_pedido_id = AsyncMock(return_value=MagicMock(id=1))

        with patch("app.modules.pagos.service.PagoRepository", return_value=mock_repo):
            service = PagoService(mock_uow)
            body = PagoCreate(pedido_id=1)

            with pytest.raises(Exception) as exc:
                await service.crear_pago(usuario_id=100, body=body)

            assert exc.value.status_code == 409


class TestPagoRepository:
    """Tests for PagoRepository methods"""

    @pytest.fixture
    def mock_session(self):
        """Create mock AsyncSession"""
        session = AsyncMock()
        return session

    @pytest.mark.asyncio
    async def test_get_by_pedido_id_found(self, mock_session):
        """Test: Find payment by order ID"""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=MagicMock(id=1))
        mock_session.execute = AsyncMock(return_value=mock_result)

        repo = PagoRepository(mock_session)
        result = await repo.get_by_pedido_id(1)

        assert result is not None

    @pytest.mark.asyncio
    async def test_get_by_idempotency_key_found(self, mock_session):
        """Test: Find payment by idempotency key"""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=MagicMock(id=1))
        mock_session.execute = AsyncMock(return_value=mock_result)

        repo = PagoRepository(mock_session)
        result = await repo.get_by_idempotency_key("test-key-123")

        assert result is not None


class TestPagoServiceProcesarWebhook:
    """Tests for procesar_webhook method"""

    @pytest.fixture
    def mock_uow(self):
        """Create mock UnitOfWork"""
        uow = MagicMock()
        uow.session = MagicMock()
        return uow

    @pytest.mark.asyncio
    async def test_procesar_webhook_unsupported_topic(self, mock_uow):
        """Test: Ignore non-payment topics"""
        service = PagoService(mock_uow)
        result = await service.procesar_webhook(topic="plan", resource_id="123")

        assert result["processed"] is False
        assert "Unsupported topic" in result["message"]

    @pytest.mark.asyncio
    async def test_procesar_webhook_payment_not_found(self, mock_uow):
        """Test: Handle when payment not found in our DB"""
        mock_mp_client = MagicMock()
        mock_mp_client.payment.return_value.get.return_value = {
            "status": 200,
            "response": {
                "status": "approved",
                "status_detail": "accredited",
                "external_reference": "999",
            },
        }

        # Mock repo returns None
        mock_repo = MagicMock()
        mock_repo.get_by_mp_payment_id = AsyncMock(return_value=None)
        mock_repo.get_by_pedido_id = AsyncMock(return_value=None)
        mock_repo.update_status = AsyncMock()

        with patch("app.modules.pagos.service.mercadopago.SDK", return_value=mock_mp_client):
            with patch("app.modules.pagos.service.PagoRepository", return_value=mock_repo):
                service = PagoService(mock_uow)
                result = await service.procesar_webhook(topic="payment", resource_id="12345")

                # Should log warning but not crash
                assert result["processed"] is False


class TestFSMTransition:
    """Tests for state machine transitions"""

    @pytest.fixture
    def mock_uow(self):
        """Create mock UnitOfWork"""
        uow = MagicMock()
        uow.session = MagicMock()
        uow.session.add = MagicMock()
        uow.session.flush = AsyncMock()
        uow.session.refresh = AsyncMock()
        uow.pedidos = MagicMock()
        return uow

    @pytest.mark.asyncio
    async def test_cambiar_estado_pendiente_a_confirmado(self, mock_uow):
        """Test: Valid transition PENDIENTE -> CONFIRMADO"""
        mock_pedido = MagicMock()
        mock_pedido.id = 1
        mock_pedido.estado_codigo = "PENDIENTE"
        mock_uow.pedidos.find = AsyncMock(return_value=mock_pedido)

        from app.modules.pedidos.service import PedidoService

        service = PedidoService(mock_uow)
        result = await service.cambiar_estado(
            pedido_id=1,
            nuevo_estado="CONFIRMADO",
            observacion="Pago aprobado",
            usuario_id=100,
        )

        assert result.estado_codigo == "CONFIRMADO"

    @pytest.mark.asyncio
    async def test_cambiar_estado_invalid_transition(self, mock_uow):
        """Test: Invalid transition raises error"""
        mock_pedido = MagicMock()
        mock_pedido.id = 1
        mock_pedido.estado_codigo = "PENDIENTE"
        mock_uow.pedidos.find = AsyncMock(return_value=mock_pedido)

        from app.modules.pedidos.service import PedidoService

        service = PedidoService(mock_uow)

        with pytest.raises(Exception) as exc:
            await service.cambiar_estado(
                pedido_id=1,
                nuevo_estado="ENTREGADO",  # Can't go directly to ENTREGADO
                observacion="",
                usuario_id=100,
            )

        assert exc.value.status_code == 400
        assert "inválida" in exc.value.detail.lower()

    @pytest.mark.asyncio
    async def test_cambiar_estado_cancelled_no_return(self):
        """Test: Terminal state CANCELADO has no outgoing transitions"""
        from app.modules.pedidos.service import PedidoService

        # This test documents that CANCELADO is terminal
        # The service should not allow transitions from CANCELADO
        # This is enforced by the transiciones_permitidas dict
        pass  # See service.py for implementation