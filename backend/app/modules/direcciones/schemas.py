"""Pydantic v2 schemas for delivery address request/response validation"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class DireccionBase(BaseModel):
    """Common address fields for Create/Read"""

    alias: Optional[str] = Field(
        None, max_length=50, description="Etiqueta opcional (max 50 chars)"
    )
    linea1: str = Field(
        ...,
        max_length=500,
        min_length=1,
        description="Dirección completa (línea 1, requerido, max 500 chars)",
    )


class DireccionCreate(DireccionBase):
    """Schema for creating a new address.

    Note: es_principal is NOT in this schema — it's auto-assigned
    by the service (first address = principal).
    """

    pass


class DireccionUpdate(BaseModel):
    """Schema for updating an address — all fields optional.

    Note: es_principal cannot be changed via PUT.
    To change the default address, use PATCH /{id}/predeterminada.
    """

    alias: Optional[str] = Field(None, max_length=50)
    linea1: Optional[str] = Field(None, max_length=500, min_length=1)


class DireccionRead(DireccionBase):
    """Schema for address response"""

    id: int
    usuario_id: int
    es_principal: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DireccionListResponse(BaseModel):
    """Paginated list response for addresses"""

    items: List[DireccionRead]
    total: int
    skip: int = Field(default=0)
    limit: int = Field(default=100)
