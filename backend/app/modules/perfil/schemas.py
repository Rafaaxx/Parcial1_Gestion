"""Pydantic schemas for the Perfil module.

Three schemas:
  - PerfilRead: Response for GET /perfil and PUT /perfil
  - PerfilUpdate: Request body for PUT /perfil
  - PasswordChange: Request body for PUT /perfil/password
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class PerfilRead(BaseModel):
    """Full profile response — NEVER includes password_hash."""

    id: int
    nombre: str
    apellido: str
    email: str
    telefono: Optional[str] = None
    roles: list[str]
    fecha_registro: datetime

    model_config = {"from_attributes": True}


class PerfilUpdate(BaseModel):
    """Profile update payload — all fields optional, at least one required."""

    nombre: Optional[str] = Field(
        default=None, min_length=2, max_length=100,
        description="Nombre del usuario",
    )
    apellido: Optional[str] = Field(
        default=None, min_length=2, max_length=100,
        description="Apellido del usuario",
    )
    telefono: Optional[str] = Field(
        default=None, max_length=20,
        description="Teléfono del usuario (opcional)",
    )


class PasswordChange(BaseModel):
    """Password change payload."""

    password_actual: str = Field(
        ..., min_length=1,
        description="Contraseña actual del usuario",
    )
    password_nueva: str = Field(
        ..., min_length=8,
        description="Nueva contraseña (mínimo 8 caracteres)",
    )


class PasswordChangeResponse(BaseModel):
    """Response after successful password change."""

    message: str = "Contraseña actualizada exitosamente"
    requires_relogin: bool = True
