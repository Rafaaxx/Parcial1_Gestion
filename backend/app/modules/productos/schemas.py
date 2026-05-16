"""Pydantic schemas for Producto validation and API responses"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

# --- Schemas for Categoria (used as nested responses) ---


class CategoriaBasica(BaseModel):
    """Basic category info for nested responses in Producto schemas"""

    id: int = Field(..., description="ID de la categoría")
    nombre: str = Field(..., description="Nombre de la categoría")

    class Config:
        from_attributes = True


# --- Schemas for Ingrediente (used as nested responses) ---


class IngredienteBasico(BaseModel):
    """Basic ingredient info for nested responses in Producto schemas"""

    id: int = Field(..., description="ID del ingrediente")
    nombre: str = Field(..., description="Nombre del ingrediente")
    es_alergeno: bool = Field(..., description="¿Es un alérgeno?")

    class Config:
        from_attributes = True


# --- ProductoIngrediente schemas ---


class ProductoIngredienteRead(BaseModel):
    """Schema for reading a product-ingredient association"""

    id: int = Field(..., description="ID de la asociación")
    ingrediente_id: int = Field(..., description="ID del ingrediente")
    es_removible: bool = Field(..., description="¿Se puede remover en el pedido?")
    ingrediente: Optional[IngredienteBasico] = Field(None, description="Detalles del ingrediente")

    class Config:
        from_attributes = True


# --- ProductoCategoria schemas ---


class ProductoCategoriaRead(BaseModel):
    """Schema for reading a product-category association"""

    id: int = Field(..., description="ID de la asociación")
    categoria_id: int = Field(..., description="ID de la categoría")
    es_principal: bool = Field(..., description="¿Es la categoría principal?")
    categoria: Optional[CategoriaBasica] = Field(None, description="Detalles de la categoría")

    class Config:
        from_attributes = True


# --- Producto schemas ---


class ProductoCreate(BaseModel):
    """Schema for creating a new product"""

    nombre: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Nombre del producto (único entre activos)",
    )
    descripcion: Optional[str] = Field(None, description="Descripción del producto")
    precio_base: Decimal = Field(
        ...,
        ge=Decimal("0.00"),
        decimal_places=2,
        description="Precio base del producto (>= 0)",
    )
    stock_cantidad: int = Field(default=0, ge=0, description="Cantidad en stock inicial (>= 0)")
    disponible: bool = Field(default=True, description="¿Está disponible para venta?")
    imagen: Optional[str] = Field(None, max_length=500, description="URL de la imagen del producto")

    @field_validator("nombre")
    @classmethod
    def trim_nombre(cls, v: str) -> str:
        """Trim and validate product name"""
        if v:
            v = v.strip()
        if not v:
            raise ValueError("nombre cannot be empty or whitespace-only")
        return v

    @field_validator("precio_base")
    @classmethod
    def validate_precio(cls, v: Decimal) -> Decimal:
        """Ensure price has at most 2 decimal places"""
        if v < Decimal("0.00"):
            raise ValueError("precio_base cannot be negative")
        return round(v, 2)


class ProductoUpdate(BaseModel):
    """Schema for updating an existing product (all fields optional)"""

    nombre: Optional[str] = Field(
        None, min_length=1, max_length=200, description="Nombre del producto"
    )
    descripcion: Optional[str] = Field(None, description="Descripción del producto")
    precio_base: Optional[Decimal] = Field(
        None,
        ge=Decimal("0.00"),
        decimal_places=2,
        description="Precio base del producto",
    )
    stock_cantidad: Optional[int] = Field(None, description="Cantidad en stock (solo para admin)")
    disponible: Optional[bool] = Field(None, description="¿Está disponible para venta?")
    imagen: Optional[str] = Field(None, max_length=500, description="URL de la imagen del producto")

    @field_validator("nombre")
    @classmethod
    def trim_nombre(cls, v: Optional[str]) -> Optional[str]:
        """Trim and validate product name if provided"""
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("nombre cannot be empty or whitespace-only")
        return v


class StockUpdate(BaseModel):
    """Schema for updating product stock"""

    stock_cantidad: int = Field(..., ge=0, description="Nueva cantidad en stock (>= 0)")


class DisponibilidadUpdate(BaseModel):
    """Schema for toggling product availability"""

    disponible: bool = Field(..., description="Nuevo estado de disponibilidad")


class ProductoRead(BaseModel):
    """Schema for reading a product (compact response for lists)"""

    id: int = Field(..., description="ID del producto")
    nombre: str = Field(..., description="Nombre del producto")
    descripcion: Optional[str] = Field(None, description="Descripción")
    precio_base: Decimal = Field(..., description="Precio base")
    stock_cantidad: Optional[int] = Field(None, description="Cantidad en stock (solo para admin)")
    disponible: bool = Field(..., description="¿Está disponible?")
    imagen: Optional[str] = Field(None, description="URL de imagen")
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: datetime = Field(..., description="Última modificación")
    deleted_at: Optional[datetime] = Field(None, description="Fecha de eliminación (soft delete)")

    class Config:
        from_attributes = True


class ProductoDetail(BaseModel):
    """Schema for product detail response (full info with associations)"""

    id: int = Field(..., description="ID del producto")
    nombre: str = Field(..., description="Nombre del producto")
    descripcion: Optional[str] = Field(None, description="Descripción")
    precio_base: Decimal = Field(..., description="Precio base")
    disponible: bool = Field(..., description="¿Está disponible?")
    stock_cantidad: int = Field(..., description="Cantidad en stock")
    imagen: Optional[str] = Field(None, description="URL de imagen")
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: datetime = Field(..., description="Última modificación")
    categorias: List[ProductoCategoriaRead] = Field(
        default_factory=list, description="Categorías asociadas"
    )
    ingredientes: List[ProductoIngredienteRead] = Field(
        default_factory=list, description="Ingredientes asociados"
    )

    class Config:
        from_attributes = True


class ProductoListItem(BaseModel):
    """
    Schema for product in list responses.

    Differs from ProductoRead:
    - Public endpoint: NO stock_cantidad (spec: "No revelar stock exacto en público")
    - Admin endpoint: includes stock_cantidad
    """

    id: int = Field(..., description="ID del producto")
    nombre: str = Field(..., description="Nombre del producto")
    descripcion: Optional[str] = Field(None, description="Descripción")
    precio_base: Decimal = Field(..., description="Precio base")
    stock_cantidad: Optional[int] = Field(None, description="Cantidad en stock")
    disponible: bool = Field(..., description="¿Está disponible?")
    imagen: Optional[str] = Field(None, description="URL de imagen")
    categorias: List[CategoriaBasica] = Field(
        default_factory=list, description="Categorías asociadas"
    )
    ingredientes: List[IngredienteBasico] = Field(
        default_factory=list, description="Ingredientes (para display de alérgenos)"
    )

    class Config:
        from_attributes = True


class ProductoListResponse(BaseModel):
    """Schema for paginated product list response"""

    items: List[ProductoListItem] = Field(..., description="Lista de productos")
    total: int = Field(..., description="Total de productos")
    skip: int = Field(..., description="Offset utilizado")
    limit: int = Field(..., description="Límite utilizado")


# --- Association schemas ---


class ProductoCategoriaCreate(BaseModel):
    """Schema for adding a category to a product"""

    categoria_id: int = Field(..., description="ID de la categoría a asociar")
    es_principal: bool = Field(default=False, description="¿Es la categoría principal?")


class ProductoIngredienteCreate(BaseModel):
    """Schema for adding an ingredient to a product"""

    ingrediente_id: int = Field(..., description="ID del ingrediente a asociar")
    es_removible: bool = Field(default=True, description="¿El cliente puede removerlo del pedido?")
