"""AdminService — stateless service for admin operations.

Handles:
  - Metrics aggregation (resumen, ventas, productos-top, pedidos-por-estado)
  - User management (list, edit roles, activate/deactivate)
"""

import logging
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from app.exceptions import ConflictError, ForbiddenError, NotFoundError
from app.modules.admin.repository import AdminRepository
from app.modules.admin.schemas import (
    PedidoEstadoRead,
    ProductoTopRead,
    ResumenMetricasRead,
    UsuarioAdminListResponse,
    UsuarioAdminRead,
    VentaPeriodoRead,
)
from app.security import create_access_token
from app.uow import UnitOfWork

logger = logging.getLogger(__name__)


class AdminService:
    """Stateless admin service."""

    def __init__(self):
        pass

    # ═══════════════════════════════════════════════════════════════════════════
    # Metrics
    # ═══════════════════════════════════════════════════════════════════════════

    async def get_resumen(
        self,
        uow: UnitOfWork,
        repo: AdminRepository,
        desde: Optional[str] = None,
        hasta: Optional[str] = None,
    ) -> dict:
        """Get dashboard metrics summary."""
        total_ventas = await repo.get_total_ventas(desde, hasta)
        cantidad_pedidos = await repo.get_cantidad_pedidos(desde, hasta)
        pedidos_por_estado = await repo.get_pedidos_por_estado(desde, hasta)
        usuarios_registrados = await repo.get_usuarios_registrados()
        top_productos = await repo.get_productos_mas_vendidos(top=5, desde=desde, hasta=hasta)

        return {
            "total_ventas": total_ventas,
            "cantidad_pedidos": cantidad_pedidos,
            "pedidos_por_estado": pedidos_por_estado,
            "usuarios_registrados": usuarios_registrados,
            "productos_mas_vendidos": [
                {
                    "producto_id": p["producto_id"],
                    "nombre": p["nombre"],
                    "cantidad_total": p["cantidad_total"],
                    "ingreso_total": p["ingreso_total"],
                }
                for p in top_productos
            ],
        }

    async def get_ventas(
        self,
        uow: UnitOfWork,
        repo: AdminRepository,
        granularidad: str,
        desde: Optional[str] = None,
        hasta: Optional[str] = None,
    ) -> list[dict]:
        """Get sales by period."""
        return await repo.get_ventas_por_periodo(granularidad, desde, hasta)

    async def get_productos_top(
        self,
        uow: UnitOfWork,
        repo: AdminRepository,
        top: int = 10,
        desde: Optional[str] = None,
        hasta: Optional[str] = None,
    ) -> list[dict]:
        """Get top selling products."""
        return await repo.get_productos_mas_vendidos(top=top, desde=desde, hasta=hasta)

    async def get_pedidos_por_estado(
        self,
        uow: UnitOfWork,
        repo: AdminRepository,
        desde: Optional[str] = None,
        hasta: Optional[str] = None,
    ) -> list[dict]:
        """Get order distribution by state."""
        return await repo.get_pedidos_por_estado(desde, hasta)

    # ═══════════════════════════════════════════════════════════════════════════
    # User Management
    # ═══════════════════════════════════════════════════════════════════════════

    async def list_usuarios(
        self,
        repo: AdminRepository,
        skip: int = 0,
        limit: int = 20,
        busqueda: Optional[str] = None,
        rol: Optional[str] = None,
        activo: Optional[bool] = None,
    ) -> dict:
        """List users with pagination, search, and filters."""
        users, total = await repo.list_usuarios(
            skip=skip,
            limit=limit,
            busqueda=busqueda,
            rol=rol,
            activo=activo,
        )

        items = []
        for u in users:
            roles = [ur.rol_codigo for ur in (u.usuario_roles or [])]
            items.append(
                {
                    "id": u.id,
                    "nombre": f"{u.nombre} {u.apellido}".strip(),
                    "email": u.email,
                    "roles": roles,
                    "activo": u.activo,
                    "creado_en": u.created_at.isoformat() if u.created_at else None,
                    "ultimo_login": None,
                }
            )

        return {
            "items": items,
            "total": total,
            "skip": skip,
            "limit": limit,
        }

    async def update_usuario(
        self,
        repo: AdminRepository,
        usuario_id: int,
        nombre: Optional[str] = None,
        email: Optional[str] = None,
        roles_codes: Optional[list[str]] = None,
    ) -> dict:
        """Update user data and/or roles.

        Validates:
          - User exists
          - Cannot remove ADMIN role from the last ADMIN
        """
        user = await repo.get_usuario_with_roles(usuario_id)
        if not user:
            raise NotFoundError("Usuario no encontrado")

        # Update fields
        if nombre is not None:
            parts = nombre.split(" ", 1)
            user.nombre = parts[0]
            user.apellido = parts[1] if len(parts) > 1 else ""
        if email is not None:
            user.email = email

        # Update roles
        if roles_codes is not None:
            current_roles = {ur.rol_codigo for ur in (user.usuario_roles or [])}
            had_admin = "ADMIN" in current_roles
            new_has_admin = "ADMIN" in roles_codes

            # If removing ADMIN from the last remaining admin
            if had_admin and not new_has_admin:
                admin_count = await repo.get_admin_count()
                if admin_count <= 1:
                    raise ConflictError("No se puede remover el último administrador del sistema")

            await repo.update_usuario_roles(usuario_id, roles_codes)

            # Revoke all refresh tokens on role change
            await repo.revoke_user_tokens(usuario_id)

        # Expire session identity map and re-fetch to get fresh relationship data
        repo.session.expire_all()
        user = await repo.get_usuario_with_roles(usuario_id)

        roles = [ur.rol_codigo for ur in (user.usuario_roles or [])]
        return {
            "id": user.id,
            "nombre": f"{user.nombre} {user.apellido}".strip(),
            "email": user.email,
            "roles": roles,
            "activo": user.activo,
            "creado_en": user.created_at.isoformat() if user.created_at else None,
            "ultimo_login": None,
        }

    async def update_usuario_estado(
        self,
        repo: AdminRepository,
        target_usuario_id: int,
        current_usuario_id: int,
        activo: bool,
    ) -> dict:
        """Activate or deactivate a user.

        Validates:
          - Cannot deactivate yourself
          - User exists
        """
        if target_usuario_id == current_usuario_id:
            raise ConflictError("No puedes desactivarte a ti mismo")

        user = await repo.get_usuario_with_roles(target_usuario_id)
        if not user:
            raise NotFoundError("Usuario no encontrado")

        user.activo = activo
        await repo.session.flush()

        # Revoke tokens if deactivated
        if not activo:
            await repo.revoke_user_tokens(target_usuario_id)

        # Re-fetch user to get fresh data
        user = await repo.get_usuario_with_roles(target_usuario_id)

        roles = [ur.rol_codigo for ur in (user.usuario_roles or [])]
        return {
            "id": user.id,
            "nombre": f"{user.nombre} {user.apellido}".strip(),
            "email": user.email,
            "roles": roles,
            "activo": user.activo,
            "creado_en": user.created_at.isoformat() if user.created_at else None,
            "ultimo_login": None,
        }
