"""AdminRepository — metrics aggregation queries and admin user operations."""

import logging
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from sqlalchemy import and_, case, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.pedido import DetallePedido, Pedido
from app.models.producto import Producto
from app.models.rol import Rol
from app.models.usuario import Usuario
from app.models.usuario_rol import UsuarioRol

logger = logging.getLogger(__name__)


class AdminRepository:
    """Repository for admin operations — metrics and user management.

    Uses raw SQLAlchemy queries for aggregation (per D4 in design.md:
    all aggregations run in PostgreSQL, not Python).
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    # ═══════════════════════════════════════════════════════════════════════════
    # Metrics Queries
    # ═══════════════════════════════════════════════════════════════════════════

    async def get_total_ventas(
        self, desde: Optional[str] = None, hasta: Optional[str] = None
    ) -> Decimal:
        """SUM of total from ENTREGADO orders."""
        query = select(func.coalesce(func.sum(Pedido.total), 0)).where(
            Pedido.estado_codigo == "ENTREGADO",
            Pedido.deleted_at.is_(None),
        )
        if desde:
            query = query.where(Pedido.created_at >= desde)
        if hasta:
            query = query.where(Pedido.created_at <= hasta)
        result = await self.session.execute(query)
        val = result.scalar()
        return Decimal(str(val)) if val is not None else Decimal("0.00")

    async def get_cantidad_pedidos(
        self, desde: Optional[str] = None, hasta: Optional[str] = None
    ) -> int:
        """Count total orders in period."""
        query = select(func.count(Pedido.id)).where(Pedido.deleted_at.is_(None))
        if desde:
            query = query.where(Pedido.created_at >= desde)
        if hasta:
            query = query.where(Pedido.created_at <= hasta)
        result = await self.session.execute(query)
        return result.scalar() or 0

    async def get_pedidos_por_estado(
        self, desde: Optional[str] = None, hasta: Optional[str] = None
    ) -> list[dict]:
        """Group orders by estado_codigo with count."""
        # Use raw SQL for proper GROUP BY with JOIN
        total_query = select(func.count(Pedido.id)).where(Pedido.deleted_at.is_(None))
        if desde:
            total_query = total_query.where(Pedido.created_at >= desde)
        if hasta:
            total_query = total_query.where(Pedido.created_at <= hasta)
        total_result = await self.session.execute(total_query)
        total = total_result.scalar() or 0

        query = (
            select(
                Pedido.estado_codigo,
                func.count(Pedido.id).label("cantidad"),
            )
            .where(Pedido.deleted_at.is_(None))
            .group_by(Pedido.estado_codigo)
        )
        if desde:
            query = query.where(Pedido.created_at >= desde)
        if hasta:
            query = query.where(Pedido.created_at <= hasta)

        result = await self.session.execute(query)
        rows = result.all()

        return [
            {
                "estado": row.estado_codigo,
                "cantidad": row.cantidad,
                "porcentaje": (round((row.cantidad / total * 100), 2) if total > 0 else 0.0),
            }
            for row in rows
        ]

    async def get_usuarios_registrados(self) -> int:
        """Count all non-deleted users."""
        query = select(func.count(Usuario.id)).where(Usuario.deleted_at.is_(None))
        result = await self.session.execute(query)
        return result.scalar() or 0

    async def get_productos_mas_vendidos(
        self, top: int = 5, desde: Optional[str] = None, hasta: Optional[str] = None
    ) -> list[dict]:
        """Top N products by quantity sold (from ENTREGADO orders)."""
        query = (
            select(
                DetallePedido.producto_id,
                Producto.nombre,
                func.sum(DetallePedido.cantidad).label("cantidad_total"),
                func.sum(DetallePedido.precio_snapshot * DetallePedido.cantidad).label(
                    "ingreso_total"
                ),
            )
            .join(Pedido, DetallePedido.pedido_id == Pedido.id)
            .join(Producto, DetallePedido.producto_id == Producto.id)
            .where(
                Pedido.estado_codigo == "ENTREGADO",
                Pedido.deleted_at.is_(None),
                Producto.deleted_at.is_(None),
            )
            .group_by(DetallePedido.producto_id, Producto.nombre)
            .order_by(text("cantidad_total DESC"))
            .limit(top)
        )
        if desde:
            query = query.where(Pedido.created_at >= desde)
        if hasta:
            query = query.where(Pedido.created_at <= hasta)

        result = await self.session.execute(query)
        rows = result.all()

        return [
            {
                "producto_id": row.producto_id,
                "nombre": row.nombre,
                "cantidad_total": int(row.cantidad_total),
                "ingreso_total": (
                    Decimal(str(row.ingreso_total)) if row.ingreso_total else Decimal("0.00")
                ),
            }
            for row in rows
        ]

    async def get_ventas_por_periodo(
        self,
        granularidad: str,
        desde: Optional[str] = None,
        hasta: Optional[str] = None,
    ) -> list[dict]:
        """Sales aggregated by time period.

        Uses strftime for SQLite compatibility (tests) and date_trunc for PostgreSQL.
        Detects which to use based on dialect.
        """
        dialect = self.session.bind.dialect.name if self.session.bind else "sqlite"

        if granularidad == "dia":
            if dialect == "sqlite":
                period = func.strftime("%Y-%m-%d", Pedido.created_at)
            else:
                period = func.date_trunc("day", Pedido.created_at)
        elif granularidad == "semana":
            if dialect == "sqlite":
                period = func.strftime("%Y-%W", Pedido.created_at)
            else:
                period = func.date_trunc("week", Pedido.created_at)
        else:
            if dialect == "sqlite":
                period = func.strftime("%Y-%m", Pedido.created_at)
            else:
                period = func.date_trunc("month", Pedido.created_at)

        query = (
            select(
                period.label("periodo"),
                func.sum(Pedido.total).label("monto_total"),
                func.count(Pedido.id).label("cantidad_pedidos"),
            )
            .where(
                Pedido.estado_codigo == "ENTREGADO",
                Pedido.deleted_at.is_(None),
            )
            .group_by(text("periodo"))
            .order_by(text("periodo ASC"))
        )
        if desde:
            query = query.where(Pedido.created_at >= desde)
        if hasta:
            query = query.where(Pedido.created_at <= hasta)

        result = await self.session.execute(query)
        rows = result.all()

        return [
            {
                "periodo": str(row.periodo),
                "monto_total": (
                    Decimal(str(row.monto_total)) if row.monto_total else Decimal("0.00")
                ),
                "cantidad_pedidos": int(row.cantidad_pedidos),
            }
            for row in rows
        ]

    # ═══════════════════════════════════════════════════════════════════════════
    # Admin User Management Queries
    # ═══════════════════════════════════════════════════════════════════════════

    async def list_usuarios(
        self,
        skip: int = 0,
        limit: int = 20,
        busqueda: Optional[str] = None,
        rol: Optional[str] = None,
        activo: Optional[bool] = None,
    ) -> tuple[list[Usuario], int]:
        """List users with pagination, search, and filters.

        Returns (users, total_count).
        """
        base_query = select(Usuario).where(Usuario.deleted_at.is_(None))
        count_query = select(func.count(Usuario.id)).where(Usuario.deleted_at.is_(None))

        # Search by name or email (ILIKE)
        if busqueda:
            pattern = f"%{busqueda}%"
            filter_clause = and_(
                Usuario.deleted_at.is_(None),
                (Usuario.nombre.ilike(pattern)) | (Usuario.email.ilike(pattern)),
            )
            base_query = base_query.where(filter_clause)
            count_query = count_query.where(filter_clause)

        # Filter by role code — use EXISTS subquery to avoid row duplication
        if rol:
            from sqlalchemy import exists

            role_subq = (
                select(UsuarioRol.usuario_id)
                .where(UsuarioRol.rol_codigo == rol)
                .where(UsuarioRol.usuario_id == Usuario.id)
            )
            base_query = base_query.where(exists(role_subq))
            count_query = count_query.where(exists(role_subq))

        # Filter by active status
        if activo is not None:
            base_query = base_query.where(Usuario.activo == activo)
            count_query = count_query.where(Usuario.activo == activo)

        # Get total count
        count_result = await self.session.execute(count_query)
        total = count_result.scalar() or 0

        # Add ordering and pagination
        base_query = (
            base_query.options(selectinload(Usuario.usuario_roles))
            .order_by(Usuario.id)
            .offset(skip)
            .limit(limit)
        )

        result = await self.session.execute(base_query)
        # Use unique() to handle joined loading
        users = list(result.unique().scalars().all())

        return users, total

    async def get_usuario_with_roles(self, usuario_id: int) -> Optional[Usuario]:
        """Get a single user with roles eagerly loaded."""
        query = (
            select(Usuario)
            .where(Usuario.id == usuario_id, Usuario.deleted_at.is_(None))
            .options(selectinload(Usuario.usuario_roles))
        )
        result = await self.session.execute(query)
        return result.unique().scalar_one_or_none()

    async def get_admin_count(self) -> int:
        """Count active ADMIN users."""
        query = (
            select(func.count(Usuario.id))
            .select_from(Usuario)
            .join(UsuarioRol, UsuarioRol.usuario_id == Usuario.id)
            .where(
                Usuario.deleted_at.is_(None),
                Usuario.activo.is_(True),
                UsuarioRol.rol_codigo == "ADMIN",
            )
        )
        result = await self.session.execute(query)
        return result.scalar() or 0

    async def update_usuario_roles(self, usuario_id: int, roles_codes: list[str]) -> None:
        """Replace all roles for a user by role codes.

        The roles_codes are the role codes (ADMIN, STOCK, PEDIDOS, CLIENT).
        """
        # Remove existing roles
        delete_query = select(UsuarioRol).where(UsuarioRol.usuario_id == usuario_id)
        result = await self.session.execute(delete_query)
        existing = result.scalars().all()
        for ur in existing:
            await self.session.delete(ur)

        for codigo in roles_codes:
            ur = UsuarioRol(usuario_id=usuario_id, rol_codigo=codigo)
            self.session.add(ur)

        await self.session.flush()

    async def revoke_user_tokens(self, usuario_id: int) -> None:
        """Revoke all active refresh tokens for a user."""
        from app.modules.refreshtokens.model import RefreshToken

        now = datetime.now(timezone.utc)
        stmt = select(RefreshToken).where(
            RefreshToken.usuario_id == usuario_id,
            RefreshToken.revoked_at.is_(None),
        )
        result = await self.session.execute(stmt)
        tokens = result.scalars().all()
        for token in tokens:
            token.revoked_at = now
            self.session.add(token)
        await self.session.flush()
