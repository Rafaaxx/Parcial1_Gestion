"""Integration tests for seed data: roles, estados, formas_pago, admin user.

These tests verify that the seed data defined in ``app.db.seed``
can be inserted into the database and that the operation is idempotent.

They use the real domain models (Rol, EstadoPedido, etc.) so those tables
are automatically created by ``Base.metadata.create_all`` in the session
fixture.
"""

import pytest
from passlib.hash import bcrypt
from pytest import mark
from sqlalchemy import func, select

from app.db.seed import (
    ADMIN_APELLIDO,
    ADMIN_EMAIL,
    ADMIN_NOMBRE,
    ADMIN_PASSWORD,
    ESTADOS_PEDIDO,
    FORMAS_PAGO,
    ROLES,
)
from app.models.estado_pedido import EstadoPedido
from app.models.forma_pago import FormaPago
from app.models.rol import Rol
from app.models.usuario import Usuario
from app.models.usuario_rol import UsuarioRol

pytestmark = mark.asyncio


async def _seed_roles(session):
    """Insert seed roles using ORM."""
    for codigo, descripcion in ROLES:
        existing = await session.get(Rol, codigo)
        if existing is None:
            session.add(Rol(codigo=codigo, descripcion=descripcion))
    await session.flush()


async def _seed_estados(session):
    """Insert seed estados_pedido using ORM."""
    for codigo, descripcion, orden, es_terminal in ESTADOS_PEDIDO:
        existing = await session.get(EstadoPedido, codigo)
        if existing is None:
            session.add(
                EstadoPedido(
                    codigo=codigo,
                    descripcion=descripcion,
                    orden=orden,
                    es_terminal=es_terminal,
                )
            )
    await session.flush()


async def _seed_formas_pago(session):
    """Insert seed formas_pago using ORM."""
    for codigo, descripcion, habilitado in FORMAS_PAGO:
        existing = await session.get(FormaPago, codigo)
        if existing is None:
            session.add(FormaPago(codigo=codigo, descripcion=descripcion, habilitado=habilitado))
    await session.flush()


async def _seed_admin(session):
    """Insert admin user with ADMIN role."""
    result = await session.execute(select(Usuario).where(Usuario.email == ADMIN_EMAIL))
    user = result.scalar_one_or_none()
    if user is None:
        password_hash = bcrypt.hash(ADMIN_PASSWORD)
        user = Usuario(
            email=ADMIN_EMAIL,
            password_hash=password_hash,
            nombre=ADMIN_NOMBRE,
            apellido=ADMIN_APELLIDO,
            activo=True,
        )
        session.add(user)
        await session.flush()

        # Assign ADMIN role
        session.add(UsuarioRol(usuario_id=user.id, rol_codigo="ADMIN"))
        await session.flush()


# ── Tests ────────────────────────────────────────────────────────────────────


async def test_roles_exist(test_db_session):
    """After seeding, all 4 roles exist."""
    await _seed_roles(test_db_session)
    result = await test_db_session.execute(select(func.count()).select_from(Rol))
    count = result.scalar()
    assert count == 4, f"Expected 4 roles, got {count}"


async def test_estados_exist(test_db_session):
    """After seeding, all 6 estado_pedido records exist."""
    await _seed_estados(test_db_session)
    result = await test_db_session.execute(select(func.count()).select_from(EstadoPedido))
    count = result.scalar()
    assert count == 6, f"Expected 6 estados, got {count}"


async def test_formas_pago_exist(test_db_session):
    """After seeding, all 3 formas_pago records exist."""
    await _seed_formas_pago(test_db_session)
    result = await test_db_session.execute(select(func.count()).select_from(FormaPago))
    count = result.scalar()
    assert count == 3, f"Expected 3 formas de pago, got {count}"


async def test_admin_user_exists(test_db_session):
    """After seeding, admin user exists with ADMIN role."""
    await _seed_admin(test_db_session)

    # Verify user
    result = await test_db_session.execute(select(Usuario).where(Usuario.email == ADMIN_EMAIL))
    user = result.scalar_one_or_none()
    assert user is not None, "Admin user not found"
    assert user.nombre == ADMIN_NOMBRE
    assert user.apellido == ADMIN_APELLIDO
    assert user.activo is True

    # Verify password hash
    assert bcrypt.verify(ADMIN_PASSWORD, user.password_hash), "Password hash does not match"

    # Verify ADMIN role assigned
    result = await test_db_session.execute(
        select(UsuarioRol).where(
            UsuarioRol.usuario_id == user.id,
            UsuarioRol.rol_codigo == "ADMIN",
        )
    )
    role_assignment = result.scalar_one_or_none()
    assert role_assignment is not None, "Admin role not assigned"


async def test_idempotency(test_db_session):
    """Seeding twice does not create duplicate records."""
    # First pass
    await _seed_roles(test_db_session)
    await _seed_estados(test_db_session)
    await _seed_formas_pago(test_db_session)

    # Second pass (should be idempotent)
    await _seed_roles(test_db_session)
    await _seed_estados(test_db_session)
    await _seed_formas_pago(test_db_session)

    # Verify counts remained the same
    for model, expected in [
        (Rol, 4),
        (EstadoPedido, 6),
        (FormaPago, 3),
    ]:
        result = await test_db_session.execute(select(func.count()).select_from(model))
        count = result.scalar()
        assert (
            count == expected
        ), f"Idempotency failed for {model.__name__}: expected {expected}, got {count}"
