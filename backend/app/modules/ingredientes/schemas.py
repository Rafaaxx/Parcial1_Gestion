"""Pydantic schemas for ingredient validation and API responses"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class IngredienteCreate(BaseModel):
    """Schema for creating a new ingredient"""

    nombre: str = Field(..., min_length=1, max_length=255, description="Nombre del ingrediente")
    es_alergeno: bool = Field(default=False, description="¿Es un alérgeno?")

    @field_validator("nombre")
    @classmethod
    def trim_nombre(cls, v: str) -> str:
        """Trim whitespace from ingredient name"""
        if v:
            v = v.strip()
        if not v:
            raise ValueError("nombre cannot be empty or whitespace-only")
        return v


class IngredienteUpdate(BaseModel):
    """Schema for updating an ingredient"""

    nombre: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Nombre del ingrediente"
    )
    es_alergeno: Optional[bool] = Field(None, description="¿Es un alérgeno?")

    @field_validator("nombre")
    @classmethod
    def trim_nombre(cls, v: Optional[str]) -> Optional[str]:
        """Trim whitespace from ingredient name if provided"""
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("nombre cannot be empty or whitespace-only")
        return v


class IngredienteRead(BaseModel):
    """Schema for reading an ingredient (full response)"""

    id: int = Field(..., description="ID único del ingrediente")
    nombre: str = Field(..., description="Nombre del ingrediente")
    es_alergeno: bool = Field(..., description="¿Es un alérgeno?")
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: datetime = Field(..., description="Fecha de última actualización")
    deleted_at: Optional[datetime] = Field(None, description="Fecha de eliminación (soft delete)")

    class Config:
        from_attributes = True


class IngredienteListResponse(BaseModel):
    """Schema for paginated list response"""

    items: List[IngredienteRead] = Field(..., description="Lista de ingredientes")
    total: int = Field(..., description="Total de ingredientes activos")
    skip: int = Field(..., description="Offset utilizado")
    limit: int = Field(..., description="Límite utilizado")
