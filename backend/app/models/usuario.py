"""Usuario model — system users with soft delete"""
from sqlmodel import SQLModel, Field
from typing import Optional
from app.models.mixins import BaseModel


class Usuario(BaseModel, table=True):
    __tablename__ = "usuarios"
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(max_length=254, unique=True, nullable=False)
    password_hash: str = Field(max_length=60, nullable=False)
    nombre: str = Field(max_length=100, nullable=False)
    apellido: str = Field(max_length=100, nullable=False)
    telefono: Optional[str] = Field(default=None, max_length=20)
    activo: bool = Field(default=True)
