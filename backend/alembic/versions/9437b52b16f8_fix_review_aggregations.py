"""Fix review aggregations

Revision ID: 9437b52b16f8
Revises: 15b4e3c55e9e
Create Date: 2026-04-11 22:48:14.134187

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '9437b52b16f8'
down_revision: Union[str, None] = '15b4e3c55e9e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        UPDATE produtos
        SET
            total_avaliacoes = COALESCE((
                SELECT COUNT(ap.id_avaliacao)
                FROM avaliacoes_pedidos ap
                JOIN (SELECT DISTINCT id_pedido, id_produto FROM itens_pedidos) ip ON ip.id_pedido = ap.id_pedido
                WHERE ip.id_produto = produtos.id_produto
            ), 0),
            avaliacao_media = (
                SELECT AVG(ap.avaliacao)
                FROM avaliacoes_pedidos ap
                JOIN (SELECT DISTINCT id_pedido, id_produto FROM itens_pedidos) ip ON ip.id_pedido = ap.id_pedido
                WHERE ip.id_produto = produtos.id_produto
            )
    """)

def downgrade() -> None:
    pass
