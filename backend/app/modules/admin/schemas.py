"""Admin Pydantic schemas for metrics and user management."""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

# ═══════════════════════════════════════════════════════════════════════════════
# Metrics schemas
# ═══════════════════════════════════════════════════════════════════════════════


class ProductoTopRead(BaseModel):
    """Top selling product."""

    producto_id: int
    nombre: str
    cantidad_total: int
    ingreso_total: Decimal


class ResumenMetricasRead(BaseModel):
    """Dashboard metrics summary."""

    total_ventas: Decimal = Decimal("0.00")
    cantidad_pedidos: int = 0
    pedidos_por_estado: list[dict] = []
    usuarios_registrados: int = 0
    productos_mas_vendidos: list[ProductoTopRead] = []


class VentaPeriodoRead(BaseModel):
    """Sales aggregated by period."""

    periodo: str
    monto_total: Decimal = Decimal("0.00")
    cantidad_pedidos: int = 0


class PedidoEstadoRead(BaseModel):
    """Order distribution by state."""

    estado: str
    cantidad: int = 0
    porcentaje: float = 0.0


# ═══════════════════════════════════════════════════════════════════════════════
# Admin User Management schemas
# ═══════════════════════════════════════════════════════════════════════════════


class UsuarioAdminRead(BaseModel):
    """User data for admin views — includes roles and activity info."""

    id: int
    nombre: str
    email: EmailStr
    roles: list[str] = []
    activo: bool = True
    creado_en: Optional[datetime] = None
    ultimo_login: Optional[datetime] = None


class UsuarioAdminListResponse(BaseModel):
    """Paginated user list response."""

    items: list[UsuarioAdminRead]
    total: int
    skip: int = 0
    limit: int = 20


class UsuarioAdminUpdate(BaseModel):
    """Admin update for user data and roles."""

    nombre: Optional[str] = Field(default=None, min_length=2, max_length=80)
    email: Optional[EmailStr] = None
    roles_codes: Optional[list[str]] = None


class UsuarioEstadoUpdate(BaseModel):
    """Toggle user active/inactive status."""

    activo: bool
