"""Modelo ORM para vendedores cadastrados no e-commerce."""

from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Vendedor(Base):
    """Vendedor parceiro com localização e identificação no sistema."""

    __tablename__ = "vendedores"

    id_vendedor: Mapped[str] = mapped_column(String(32), primary_key=True)
    nome_vendedor: Mapped[str] = mapped_column(String(255))
    prefixo_cep: Mapped[str] = mapped_column(String(10))
    cidade: Mapped[str] = mapped_column(String(100))
    estado: Mapped[str] = mapped_column(String(2))
