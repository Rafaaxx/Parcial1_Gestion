"""FormaPago model — payment methods catalog"""
from sqlmodel import SQLModel, Field
from app.models.mixins import TimestampMixin


class FormaPago(TimestampMixin, SQLModel, table=True):
    __tablename__ = "formas_pago"
    codigo: str = Field(primary_key=True, max_length=20)
    descripcion: str = Field(max_length=100)
    habilitado: bool = Field(default=True)
