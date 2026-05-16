"""Producto model — product catalog with stock management and soft delete"""

from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship, SQLModel

from app.models.mixins import BaseModel

if TYPE_CHECKING:
    from app.models.categoria import Categoria
    from app.models.ingrediente import Ingrediente
    from app.models.pedido import DetallePedido


class Producto(BaseModel, table=True):
    """
    Product entity for the Food Store catalog.

    Features:
    - Product name with uniqueness constraint (case-insensitive, active only)
    - Decimal price for precision (no float)
    - Stock quantity management (>= 0)
    - Availability flag (independent of stock)
    - Optional image URL
    - Soft-delete support (deleted_at from BaseModel)
    - Timestamps (created_at, updated_at from BaseModel)
    - Many-to-many relationships with Categoria and Ingrediente via pivot tables

    Business rules:
    - precio_base >= 0 (enforced at app level)
    - stock_cantidad >= 0 (enforced at app level)
    - disponible is independent of stock: product can be visible but out of stock
    """

    __tablename__ = "productos"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(
        max_length=200,
        nullable=False,
        index=True,
        description="Nombre del producto (único entre productos activos)",
    )
    descripcion: Optional[str] = Field(default=None, description="Descripción del producto")
    precio_base: Decimal = Field(
        default=Decimal("0.00"),
        sa_column_kwargs={
            "nullable": False,
            "server_default": "0.00",
        },
        description="Precio base del producto (DECIMAL 10,2)",
    )
    stock_cantidad: int = Field(
        default=0, nullable=False, ge=0, description="Cantidad en stock (>= 0)"
    )
    disponible: bool = Field(
        default=True,
        nullable=False,
        index=True,
        description="Si el producto está disponible para venta (independiente del stock)",
    )
    imagen: Optional[str] = Field(
        default=None, max_length=500, description="URL de la imagen del producto"
    )

    # Relationships
    categorias: List["ProductoCategoria"] = Relationship(
        back_populates="producto",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "foreign_keys": "[ProductoCategoria.producto_id]",
        },
    )
    ingredientes: List["ProductoIngrediente"] = Relationship(
        back_populates="producto",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "foreign_keys": "[ProductoIngrediente.producto_id]",
        },
    )
    detalles_pedido: List["DetallePedido"] = Relationship(
        back_populates="producto",
        sa_relationship_kwargs={
            "foreign_keys": "[DetallePedido.producto_id]",
        },
    )


class ProductoCategoria(SQLModel, table=True):
    """
    Pivot table for N:M relationship between Producto and Categoria.

    Features:
    - es_principal flag: one category is the "main" category for display
    - Unique constraint on (producto_id, categoria_id) — no duplicate associations
    - CASCADE delete: if producto or categoria is deleted, association is removed
    """

    __tablename__ = "productos_categorias"

    id: Optional[int] = Field(default=None, primary_key=True)
    producto_id: int = Field(
        foreign_key="productos.id",
        nullable=False,
        index=True,
        description="ID del producto",
    )
    categoria_id: int = Field(
        foreign_key="categorias.id",
        nullable=False,
        index=True,
        description="ID de la categoría",
    )
    es_principal: bool = Field(
        default=False,
        nullable=False,
        description="Indica si esta es la categoría principal del producto",
    )

    # Relationships
    producto: "Producto" = Relationship(back_populates="categorias")
    categoria: "Categoria" = Relationship(back_populates="productos")


class ProductoIngrediente(SQLModel, table=True):
    """
    Pivot table for N:M relationship between Producto and Ingrediente.

    Features:
    - es_removible flag: customer can remove this ingredient from their order
    - Unique constraint on (producto_id, ingrediente_id) — no duplicate associations
    - CASCADE delete: if producto or ingrediente is deleted, association is removed

    Used for:
    - Order personalization (removing optional ingredients)
    - Allergen display (via Ingrediente.es_alergeno)
    """

    __tablename__ = "productos_ingredientes"

    id: Optional[int] = Field(default=None, primary_key=True)
    producto_id: int = Field(
        foreign_key="productos.id",
        nullable=False,
        index=True,
        description="ID del producto",
    )
    ingrediente_id: int = Field(
        foreign_key="ingredientes.id",
        nullable=False,
        index=True,
        description="ID del ingrediente",
    )
    es_removible: bool = Field(
        default=True,
        nullable=False,
        description="Indica si el cliente puede remover este ingrediente de su pedido",
    )

    # Relationships
    producto: "Producto" = Relationship(back_populates="ingredientes")
    ingrediente: "Ingrediente" = Relationship(back_populates="productos")
