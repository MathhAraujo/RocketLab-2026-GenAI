"""Modelo ORM para produtos do catálogo com métricas agregadas de vendas e avaliações."""

from __future__ import annotations

from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Produto(Base):
    """Produto do catálogo com dimensões físicas e agregados pré-calculados de vendas."""

    __tablename__ = "produtos"

    id_produto: Mapped[str] = mapped_column(String(32), primary_key=True)
    nome_produto: Mapped[str] = mapped_column(String(255))
    categoria_produto: Mapped[str] = mapped_column(String(100))
    peso_produto_gramas: Mapped[float | None] = mapped_column(Float, nullable=True)
    comprimento_centimetros: Mapped[float | None] = mapped_column(Float, nullable=True)
    altura_centimetros: Mapped[float | None] = mapped_column(Float, nullable=True)
    largura_centimetros: Mapped[float | None] = mapped_column(Float, nullable=True)

    total_vendas: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", nullable=False
    )
    preco_medio: Mapped[float | None] = mapped_column(Float, nullable=True)
    total_avaliacoes: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", nullable=False
    )
    avaliacao_media: Mapped[float | None] = mapped_column(Float, nullable=True)
