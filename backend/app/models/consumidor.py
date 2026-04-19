"""Modelo ORM para consumidores (clientes finais) do e-commerce."""

from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Consumidor(Base):
    """Cliente final que realiza pedidos na plataforma."""

    __tablename__ = "consumidores"

    id_consumidor: Mapped[str] = mapped_column(String(32), primary_key=True)
    prefixo_cep: Mapped[str] = mapped_column(String(10))
    nome_consumidor: Mapped[str] = mapped_column(String(255))
    cidade: Mapped[str] = mapped_column(String(100))
    estado: Mapped[str] = mapped_column(String(2))
