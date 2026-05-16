"""Categoria model — hierarchical product categories with self-referential FK"""

from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship, SQLModel

from app.models.mixins import BaseModel

if TYPE_CHECKING:
    from app.models.producto import ProductoCategoria


class Categoria(BaseModel, table=True):
    """
    Hierarchical category for product organization.

    Features:
    - Self-referential foreign key (parent_id → id) for tree structure
    - Soft-delete support (deleted_at from BaseModel)
    - Timestamps (created_at, updated_at from BaseModel)
    - Relationships for easy tree traversal
    """

    __tablename__ = "categorias"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(
        max_length=100,
        nullable=False,
        index=True,
        # NOTE: unique=True removed — replaced with partial index (uq_categorias_nombre_not_deleted)
        # Partial index allows reusing names after soft-delete: WHERE deleted_at IS NULL
        # Migration 005 handles the database constraint
    )
    descripcion: Optional[str] = Field(default=None, description="Descripción de la categoría")
    parent_id: Optional[int] = Field(
        default=None,
        foreign_key="categorias.id",
        nullable=True,
        description="ID de categoría padre (NULL para categorías raíz)",
    )

    # Relationships for tree traversal
    parent: Optional["Categoria"] = Relationship(
        back_populates="children",
        sa_relationship_kwargs={
            "remote_side": "Categoria.id",
            "foreign_keys": "[Categoria.parent_id]",
        },
    )
    children: List["Categoria"] = Relationship(
        back_populates="parent",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "foreign_keys": "[Categoria.parent_id]",
        },
    )
    # Relationships for CHANGE-06: producto-category associations
    productos: List["ProductoCategoria"] = Relationship(
        back_populates="categoria",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "foreign_keys": "[ProductoCategoria.categoria_id]",
        },
    )
