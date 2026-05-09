"""Database seed data script — creates initial catalog data.

Usage:
    python -m app.db.seed

This must be run once after ``alembic upgrade head``.
Without it, the application will not work: no roles, order states,
or payment methods exist.
"""
import asyncio
import logging
import os

from sqlalchemy import text

from app.database import async_session_factory

logger = logging.getLogger(__name__)

# ── Seed data constants ──────────────────────────────────────────────────────

ROLES = [
    ("ADMIN", "Administrador del sistema"),
    ("STOCK", "Gestor de stock"),
    ("PEDIDOS", "Gestor de pedidos"),
    ("CLIENT", "Cliente del sistema"),
]

ESTADOS_PEDIDO = [
    ("PENDIENTE", "Pedido creado, pago pendiente", 1, False),
    ("CONFIRMADO", "Pago procesado y confirmado", 2, False),
    ("EN_PREP", "En preparación en cocina", 3, False),
    ("EN_CAMINO", "Despachado al cliente", 4, False),
    ("ENTREGADO", "Entrega confirmada", 5, True),
    ("CANCELADO", "Pedido cancelado", 6, True),
]

FORMAS_PAGO = [
    ("MERCADOPAGO", "Mercado Pago", True),
    ("EFECTIVO", "Efectivo", True),
    ("TRANSFERENCIA", "Transferencia bancaria", True),
]

ADMIN_EMAIL = "admin@foodstore.com"
ADMIN_PASSWORD = os.getenv("SEED_ADMIN_PASSWORD", "Admin1234!")
ADMIN_NOMBRE = "Admin"
ADMIN_APELLIDO = "User"

# ── Raw SQL statements (PostgreSQL-compatible) ───────────────────────────────

INSERT_ROLES = text("""
    INSERT INTO roles (codigo, descripcion, created_at, updated_at)
    VALUES (:codigo, :descripcion, NOW(), NOW())
    ON CONFLICT (codigo) DO NOTHING
""")

INSERT_ESTADOS = text("""
    INSERT INTO estados_pedido (codigo, descripcion, orden, es_terminal, created_at, updated_at)
    VALUES (:codigo, :descripcion, :orden, :es_terminal, NOW(), NOW())
    ON CONFLICT (codigo) DO NOTHING
""")

INSERT_FORMAS_PAGO = text("""
    INSERT INTO formas_pago (codigo, descripcion, habilitado, created_at, updated_at)
    VALUES (:codigo, :descripcion, :habilitado, NOW(), NOW())
    ON CONFLICT (codigo) DO NOTHING
""")

INSERT_ADMIN_USER = text("""
    INSERT INTO usuarios (email, password_hash, nombre, apellido, activo, created_at, updated_at)
    VALUES (:email, :password_hash, :nombre, :apellido, true, NOW(), NOW())
    ON CONFLICT (email) DO NOTHING
""")

SELECT_ADMIN = text("SELECT id FROM usuarios WHERE email = :email")

INSERT_ADMIN_ROLE = text("""
    INSERT INTO usuarios_roles (usuario_id, rol_codigo, created_at, updated_at)
    VALUES (:usuario_id, :rol_codigo, NOW(), NOW())
    ON CONFLICT (usuario_id, rol_codigo) DO NOTHING
""")


# ── Seed logic ───────────────────────────────────────────────────────────────

async def seed_all(session_factory=None):
    """Execute seed data insertion.

    Args:
        session_factory: Optional async session factory. Defaults to the
                         app-wide ``async_session_factory``.

    This is idempotent — safe to run multiple times.
    """
    from passlib.hash import bcrypt

    if session_factory is None:
        session_factory = async_session_factory

    async with session_factory() as session:
        logger.info("🌱  Seeding database …")

        # 1. Roles ────────────────────────────────────────────────────────────
        for codigo, descripcion in ROLES:
            await session.execute(
                INSERT_ROLES,
                {"codigo": codigo, "descripcion": descripcion},
            )
        logger.info("  ✅  %d roles inserted", len(ROLES))

        # 2. Estados de pedido ────────────────────────────────────────────────
        for codigo, descripcion, orden, es_terminal in ESTADOS_PEDIDO:
            await session.execute(
                INSERT_ESTADOS,
                {
                    "codigo": codigo,
                    "descripcion": descripcion,
                    "orden": orden,
                    "es_terminal": es_terminal,
                },
            )
        logger.info("  ✅  %d estados de pedido inserted", len(ESTADOS_PEDIDO))

        # 3. Formas de pago ───────────────────────────────────────────────────
        for codigo, descripcion, habilitado in FORMAS_PAGO:
            await session.execute(
                INSERT_FORMAS_PAGO,
                {"codigo": codigo, "descripcion": descripcion, "habilitado": habilitado},
            )
        logger.info("  ✅  %d formas de pago inserted", len(FORMAS_PAGO))

        # 4. Admin user ───────────────────────────────────────────────────────
        password_hash = bcrypt.hash(ADMIN_PASSWORD)
        await session.execute(
            INSERT_ADMIN_USER,
            {
                "email": ADMIN_EMAIL,
                "password_hash": password_hash,
                "nombre": ADMIN_NOMBRE,
                "apellido": ADMIN_APELLIDO,
            },
        )

        # Fetch admin user id for role assignment
        result = await session.execute(SELECT_ADMIN, {"email": ADMIN_EMAIL})
        admin_id = result.scalar_one_or_none()
        logger.info("  ✅  Admin user created (id=%s)", admin_id)

        if admin_id is not None:
            await session.execute(
                INSERT_ADMIN_ROLE,
                {"usuario_id": admin_id, "rol_codigo": "ADMIN"},
            )
            logger.info("  ✅  Admin role assigned")

        await session.commit()
        logger.info("🌱  Seed complete!")


# ── CLI entry point ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    asyncio.run(seed_all())
