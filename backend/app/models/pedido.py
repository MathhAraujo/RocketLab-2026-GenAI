"""Modelo ORM para pedidos (cabeçalho) realizados por consumidores."""

from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Pedido(Base):
    """Cabeçalho de pedido com status, timestamps e métricas de entrega."""

    __tablename__ = "pedidos"

    id_pedido: Mapped[str] = mapped_column(String(32), primary_key=True)
    id_consumidor: Mapped[str] = mapped_column(
        String(32), ForeignKey("consumidores.id_consumidor"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(50))
    pedido_compra_timestamp: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    pedido_entregue_timestamp: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    data_estimada_entrega: Mapped[date | None] = mapped_column(Date, nullable=True)
    tempo_entrega_dias: Mapped[float | None] = mapped_column(Float, nullable=True)
    tempo_entrega_estimado_dias: Mapped[float | None] = mapped_column(Float, nullable=True)
    diferenca_entrega_dias: Mapped[float | None] = mapped_column(Float, nullable=True)
    entrega_no_prazo: Mapped[str | None] = mapped_column(String(10), nullable=True)
