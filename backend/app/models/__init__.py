"""SQLAlchemy ORM models — importados aqui para registro no metadata do Alembic."""

from app.models.avaliacao_pedido import AvaliacaoPedido
from app.models.consumidor import Consumidor
from app.models.item_pedido import ItemPedido
from app.models.pedido import Pedido
from app.models.produto import Produto
from app.models.usuario import Usuario
from app.models.vendedor import Vendedor

__all__ = [
    "AvaliacaoPedido",
    "Consumidor",
    "ItemPedido",
    "Pedido",
    "Produto",
    "Usuario",
    "Vendedor",
]
