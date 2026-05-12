"""Usuario model — system users with soft delete"""
from typing import Optional, TYPE_CHECKING, List
from sqlmodel import SQLModel, Field, Relationship
from app.models.mixins import BaseModel

if TYPE_CHECKING:
    from app.modules.refreshtokens.model import RefreshToken
    from app.models.usuario_rol import UsuarioRol
    from app.models.direccion_entrega import DireccionEntrega


class Usuario(BaseModel, table=True):
    __tablename__ = "usuarios"
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(max_length=254, unique=True, nullable=False)
    password_hash: str = Field(max_length=60, nullable=False)
    nombre: str = Field(max_length=100, nullable=False)
    apellido: str = Field(max_length=100, nullable=False)
    telefono: Optional[str] = Field(default=None, max_length=20)
    activo: bool = Field(default=True)

    # ── Relationships ─────────────────────────────────────────────────────────
    refresh_tokens: List["RefreshToken"] = Relationship(
        back_populates="usuario",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    usuario_roles: List["UsuarioRol"] = Relationship(
        back_populates="usuario",
        sa_relationship_kwargs={"foreign_keys": "UsuarioRol.usuario_id"},
    )
    direcciones: List["DireccionEntrega"] = Relationship(
        back_populates="usuario",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    pedidos: List["Pedido"] = Relationship(back_populates="usuario")
