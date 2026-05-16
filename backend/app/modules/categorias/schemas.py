"""Pydantic schemas for Categoria request/response validation"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class CategoriaBase(BaseModel):
    """Base schema with common fields"""

    nombre: str = Field(..., max_length=100, description="Nombre de la categoría")
    descripcion: Optional[str] = Field(None, description="Descripción opcional de la categoría")
    parent_id: Optional[int] = Field(
        None, description="ID de categoría padre (NULL para categorías raíz)"
    )


class CategoriaCreate(CategoriaBase):
    """Schema for creating a new category"""

    pass


class CategoriaUpdate(BaseModel):
    """Schema for updating an existing category (all fields optional)"""

    nombre: Optional[str] = Field(None, max_length=100)
    descripcion: Optional[str] = None
    parent_id: Optional[int] = None


class CategoriaRead(CategoriaBase):
    """Schema for category response"""

    id: int
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CategoriaTreeNode(BaseModel):
    """Nested tree response for GET /api/v1/categorias (recursive structure)"""

    id: int
    nombre: str
    descripcion: Optional[str] = None
    parent_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    subcategorias: List["CategoriaTreeNode"] = Field(
        default_factory=list, description="Child categories"
    )

    class Config:
        from_attributes = True


# Enable recursive model references
CategoriaTreeNode.model_rebuild()
