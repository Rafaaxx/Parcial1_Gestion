"""Ingrediente model — ingredient catalog with allergen flag and soft delete"""
from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field
from app.models.mixins import BaseModel

if TYPE_CHECKING:
    pass


class Ingrediente(BaseModel, table=True):
    """
    Ingredient entity for the product catalog.
    
    Features:
    - Allergen flagging (es_alergeno boolean)
    - Soft-delete support (deleted_at from BaseModel)
    - Timestamps (created_at, updated_at from BaseModel)
    - Unique constraint on nombre WHERE deleted_at IS NULL
    - Used in CHANGE-06 for product-ingredient associations
    """
    __tablename__ = "ingredientes"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(
        max_length=255,
        nullable=False,
        index=True,
        description="Nombre único del ingrediente (ej: Gluten, Lactosa)"
    )
    es_alergeno: bool = Field(
        default=False,
        nullable=False,
        index=True,
        description="Indica si el ingrediente es un alérgeno común"
    )
