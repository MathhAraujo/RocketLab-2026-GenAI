"""Modelo ORM para itens individuais de um pedido."""

from __future__ import annotations

from sqlalchemy import Float, ForeignKey, Integer, PrimaryKeyConstraint, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ItemPedido(Base):
    """Item de linha de um pedido, associando produto, vendedor e preços pagos."""

    __tablename__ = "itens_pedidos"

    id_pedido: Mapped[str] = mapped_column(
        String(32), ForeignKey("pedidos.id_pedido"), nullable=False
    )
    id_item: Mapped[int] = mapped_column(Integer, nullable=False)
    id_produto: Mapped[str] = mapped_column(
        String(32), ForeignKey("produtos.id_produto"), nullable=False, index=True
    )
    id_vendedor: Mapped[str] = mapped_column(
        String(32), ForeignKey("vendedores.id_vendedor"), nullable=False
    )
    preco_BRL: Mapped[float] = mapped_column(Float)  # noqa: N815 — nome do campo no banco legado
    preco_frete: Mapped[float] = mapped_column(Float)

    __table_args__ = (PrimaryKeyConstraint("id_pedido", "id_item"),)
