"""Modelo ORM para avaliações de pedidos feitas por consumidores."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class AvaliacaoPedido(Base):
    """Avaliação (review) associada a um pedido, incluindo nota, comentário e resposta do admin."""

    __tablename__ = "avaliacoes_pedidos"

    id_avaliacao: Mapped[str] = mapped_column(String(32), primary_key=True)
    id_pedido: Mapped[str] = mapped_column(
        String(32), ForeignKey("pedidos.id_pedido"), nullable=False, index=True
    )
    avaliacao: Mapped[int] = mapped_column(Integer)
    titulo_comentario: Mapped[str | None] = mapped_column(String(255), nullable=True)
    comentario: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    data_comentario: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    data_resposta: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    resposta_admin: Mapped[str | None] = mapped_column(Text, nullable=True)
    autor_resposta: Mapped[str | None] = mapped_column(String(255), nullable=True)
