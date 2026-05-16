"""Rol model — RBAC roles catalog"""

from sqlmodel import Field, SQLModel

from app.models.mixins import TimestampMixin


class Rol(TimestampMixin, SQLModel, table=True):
    __tablename__ = "roles"
    codigo: str = Field(primary_key=True, max_length=20)
    descripcion: str = Field(max_length=100)
