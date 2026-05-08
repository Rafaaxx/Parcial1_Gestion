"""UsuarioRol model — M:N user-role pivot with audit trail"""
from typing import Optional
from sqlalchemy import Column, BigInteger, ForeignKey, String
from sqlmodel import SQLModel, Field
from app.models.mixins import TimestampMixin


class UsuarioRol(TimestampMixin, SQLModel, table=True):
    __tablename__ = "usuarios_roles"
    usuario_id: int = Field(
        sa_column=Column(
            BigInteger,
            ForeignKey("usuarios.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        )
    )
    rol_codigo: str = Field(
        sa_column=Column(
            String(20),
            ForeignKey("roles.codigo", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        )
    )
    asignado_por_id: Optional[int] = Field(
        sa_column=Column(
            BigInteger,
            ForeignKey("usuarios.id", ondelete="SET NULL"),
            nullable=True,
        )
    )
