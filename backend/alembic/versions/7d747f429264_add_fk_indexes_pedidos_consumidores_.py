"""add fk indexes pedidos consumidores itens

Revision ID: 7d747f429264
Revises: 06f836d2e677
Create Date: 2026-04-19 15:37:43.358478

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '7d747f429264'
down_revision: Union[str, None] = '06f836d2e677'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # SQLite não suporta ADD COLUMN com FK nem CREATE INDEX em tabela existente para constraints;
    # recriamos as tabelas para adicionar indexes nas colunas FK de pedidos e itens_pedidos.
    # Usamos DROP IF EXISTS porque indexes anteriores podem ter nomes ligeiramente diferentes
    # dependendo do estado do banco na instalação.
    op.execute("DROP INDEX IF EXISTS ix_avaliacoes_pedidos_id_pedido")
    op.execute("DROP TABLE IF EXISTS avaliacoes_pedidos")
    op.execute("DROP INDEX IF EXISTS ix_usuarios_username")
    op.execute("DROP TABLE IF EXISTS usuarios")
    op.execute("DROP INDEX IF EXISTS ix_itens_pedidos_id_produto")
    op.execute("DROP TABLE IF EXISTS itens_pedidos")
    op.execute("DROP TABLE IF EXISTS pedidos")
    op.execute("DROP TABLE IF EXISTS consumidores")
    op.execute("DROP TABLE IF EXISTS vendedores")
    op.execute("DROP TABLE IF EXISTS produtos")

    op.create_table(
        'produtos',
        sa.Column('id_produto', sa.VARCHAR(length=32), nullable=False),
        sa.Column('nome_produto', sa.VARCHAR(length=255), nullable=False),
        sa.Column('categoria_produto', sa.VARCHAR(length=100), nullable=False),
        sa.Column('peso_produto_gramas', sa.FLOAT(), nullable=True),
        sa.Column('comprimento_centimetros', sa.FLOAT(), nullable=True),
        sa.Column('altura_centimetros', sa.FLOAT(), nullable=True),
        sa.Column('largura_centimetros', sa.FLOAT(), nullable=True),
        sa.Column('total_vendas', sa.INTEGER(), server_default=sa.text("'0'"), nullable=False),
        sa.Column('preco_medio', sa.FLOAT(), nullable=True),
        sa.Column('total_avaliacoes', sa.INTEGER(), server_default=sa.text("'0'"), nullable=False),
        sa.Column('avaliacao_media', sa.FLOAT(), nullable=True),
        sa.PrimaryKeyConstraint('id_produto'),
    )
    op.create_table(
        'vendedores',
        sa.Column('id_vendedor', sa.VARCHAR(length=32), nullable=False),
        sa.Column('nome_vendedor', sa.VARCHAR(length=255), nullable=False),
        sa.Column('prefixo_cep', sa.VARCHAR(length=10), nullable=False),
        sa.Column('cidade', sa.VARCHAR(length=100), nullable=False),
        sa.Column('estado', sa.VARCHAR(length=2), nullable=False),
        sa.PrimaryKeyConstraint('id_vendedor'),
    )
    op.create_table(
        'consumidores',
        sa.Column('id_consumidor', sa.VARCHAR(length=32), nullable=False),
        sa.Column('prefixo_cep', sa.VARCHAR(length=10), nullable=False),
        sa.Column('nome_consumidor', sa.VARCHAR(length=255), nullable=False),
        sa.Column('cidade', sa.VARCHAR(length=100), nullable=False),
        sa.Column('estado', sa.VARCHAR(length=2), nullable=False),
        sa.PrimaryKeyConstraint('id_consumidor'),
    )
    op.create_table(
        'pedidos',
        sa.Column('id_pedido', sa.VARCHAR(length=32), nullable=False),
        sa.Column('id_consumidor', sa.VARCHAR(length=32), nullable=False),
        sa.Column('status', sa.VARCHAR(length=50), nullable=False),
        sa.Column('pedido_compra_timestamp', sa.DATETIME(), nullable=True),
        sa.Column('pedido_entregue_timestamp', sa.DATETIME(), nullable=True),
        sa.Column('data_estimada_entrega', sa.DATE(), nullable=True),
        sa.Column('tempo_entrega_dias', sa.FLOAT(), nullable=True),
        sa.Column('tempo_entrega_estimado_dias', sa.FLOAT(), nullable=True),
        sa.Column('diferenca_entrega_dias', sa.FLOAT(), nullable=True),
        sa.Column('entrega_no_prazo', sa.VARCHAR(length=10), nullable=True),
        sa.ForeignKeyConstraint(['id_consumidor'], ['consumidores.id_consumidor']),
        sa.PrimaryKeyConstraint('id_pedido'),
    )
    op.create_index('ix_pedidos_id_consumidor', 'pedidos', ['id_consumidor'], unique=False)
    op.create_table(
        'itens_pedidos',
        sa.Column('id_pedido', sa.VARCHAR(length=32), nullable=False),
        sa.Column('id_item', sa.INTEGER(), nullable=False),
        sa.Column('id_produto', sa.VARCHAR(length=32), nullable=False),
        sa.Column('id_vendedor', sa.VARCHAR(length=32), nullable=False),
        sa.Column('preco_BRL', sa.FLOAT(), nullable=False),
        sa.Column('preco_frete', sa.FLOAT(), nullable=False),
        sa.ForeignKeyConstraint(['id_pedido'], ['pedidos.id_pedido']),
        sa.ForeignKeyConstraint(['id_produto'], ['produtos.id_produto']),
        sa.ForeignKeyConstraint(['id_vendedor'], ['vendedores.id_vendedor']),
        sa.PrimaryKeyConstraint('id_pedido', 'id_item'),
    )
    op.create_index('ix_itens_pedidos_id_pedido', 'itens_pedidos', ['id_pedido'], unique=False)
    op.create_index('ix_itens_pedidos_id_produto', 'itens_pedidos', ['id_produto'], unique=False)
    op.create_index('ix_itens_pedidos_id_vendedor', 'itens_pedidos', ['id_vendedor'], unique=False)
    op.create_table(
        'usuarios',
        sa.Column('id_usuario', sa.VARCHAR(length=32), nullable=False),
        sa.Column('username', sa.VARCHAR(length=255), nullable=False),
        sa.Column('hashed_password', sa.VARCHAR(length=255), nullable=False),
        sa.Column('is_admin', sa.BOOLEAN(), nullable=False),
        sa.PrimaryKeyConstraint('id_usuario'),
    )
    op.create_index('ix_usuarios_username', 'usuarios', ['username'], unique=True)
    op.create_table(
        'avaliacoes_pedidos',
        sa.Column('id_avaliacao', sa.VARCHAR(length=32), nullable=False),
        sa.Column('id_pedido', sa.VARCHAR(length=32), nullable=False),
        sa.Column('avaliacao', sa.INTEGER(), nullable=False),
        sa.Column('titulo_comentario', sa.VARCHAR(length=255), nullable=True),
        sa.Column('comentario', sa.VARCHAR(length=1000), nullable=True),
        sa.Column('data_comentario', sa.DATETIME(), nullable=True),
        sa.Column('data_resposta', sa.DATETIME(), nullable=True),
        sa.Column('resposta_admin', sa.TEXT(), nullable=True),
        sa.Column('autor_resposta', sa.VARCHAR(length=255), nullable=True),
        sa.ForeignKeyConstraint(['id_pedido'], ['pedidos.id_pedido']),
        sa.PrimaryKeyConstraint('id_avaliacao'),
    )
    op.create_index('ix_avaliacoes_pedidos_id_pedido', 'avaliacoes_pedidos', ['id_pedido'], unique=False)


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('produtos',
    sa.Column('id_produto', sa.VARCHAR(length=32), nullable=False),
    sa.Column('nome_produto', sa.VARCHAR(length=255), nullable=False),
    sa.Column('categoria_produto', sa.VARCHAR(length=100), nullable=False),
    sa.Column('peso_produto_gramas', sa.FLOAT(), nullable=True),
    sa.Column('comprimento_centimetros', sa.FLOAT(), nullable=True),
    sa.Column('altura_centimetros', sa.FLOAT(), nullable=True),
    sa.Column('largura_centimetros', sa.FLOAT(), nullable=True),
    sa.Column('total_vendas', sa.INTEGER(), server_default=sa.text("'0'"), nullable=False),
    sa.Column('preco_medio', sa.FLOAT(), nullable=True),
    sa.Column('total_avaliacoes', sa.INTEGER(), server_default=sa.text("'0'"), nullable=False),
    sa.Column('avaliacao_media', sa.FLOAT(), nullable=True),
    sa.PrimaryKeyConstraint('id_produto')
    )
    op.create_table('vendedores',
    sa.Column('id_vendedor', sa.VARCHAR(length=32), nullable=False),
    sa.Column('nome_vendedor', sa.VARCHAR(length=255), nullable=False),
    sa.Column('prefixo_cep', sa.VARCHAR(length=10), nullable=False),
    sa.Column('cidade', sa.VARCHAR(length=100), nullable=False),
    sa.Column('estado', sa.VARCHAR(length=2), nullable=False),
    sa.PrimaryKeyConstraint('id_vendedor')
    )
    op.create_table('pedidos',
    sa.Column('id_pedido', sa.VARCHAR(length=32), nullable=False),
    sa.Column('id_consumidor', sa.VARCHAR(length=32), nullable=False),
    sa.Column('status', sa.VARCHAR(length=50), nullable=False),
    sa.Column('pedido_compra_timestamp', sa.DATETIME(), nullable=True),
    sa.Column('pedido_entregue_timestamp', sa.DATETIME(), nullable=True),
    sa.Column('data_estimada_entrega', sa.DATE(), nullable=True),
    sa.Column('tempo_entrega_dias', sa.FLOAT(), nullable=True),
    sa.Column('tempo_entrega_estimado_dias', sa.FLOAT(), nullable=True),
    sa.Column('diferenca_entrega_dias', sa.FLOAT(), nullable=True),
    sa.Column('entrega_no_prazo', sa.VARCHAR(length=10), nullable=True),
    sa.ForeignKeyConstraint(['id_consumidor'], ['consumidores.id_consumidor'], ),
    sa.PrimaryKeyConstraint('id_pedido')
    )
    op.create_table('itens_pedidos',
    sa.Column('id_pedido', sa.VARCHAR(length=32), nullable=False),
    sa.Column('id_item', sa.INTEGER(), nullable=False),
    sa.Column('id_produto', sa.VARCHAR(length=32), nullable=False),
    sa.Column('id_vendedor', sa.VARCHAR(length=32), nullable=False),
    sa.Column('preco_BRL', sa.FLOAT(), nullable=False),
    sa.Column('preco_frete', sa.FLOAT(), nullable=False),
    sa.ForeignKeyConstraint(['id_pedido'], ['pedidos.id_pedido'], ),
    sa.ForeignKeyConstraint(['id_produto'], ['produtos.id_produto'], ),
    sa.ForeignKeyConstraint(['id_vendedor'], ['vendedores.id_vendedor'], ),
    sa.PrimaryKeyConstraint('id_pedido', 'id_item')
    )
    op.create_index('ix_itens_pedidos_id_produto', 'itens_pedidos', ['id_produto'], unique=False)
    op.create_table('usuarios',
    sa.Column('id_usuario', sa.VARCHAR(length=32), nullable=False),
    sa.Column('username', sa.VARCHAR(length=255), nullable=False),
    sa.Column('hashed_password', sa.VARCHAR(length=255), nullable=False),
    sa.Column('is_admin', sa.BOOLEAN(), nullable=False),
    sa.PrimaryKeyConstraint('id_usuario')
    )
    op.create_index('ix_usuarios_username', 'usuarios', ['username'], unique=1)
    op.create_table('avaliacoes_pedidos',
    sa.Column('id_avaliacao', sa.VARCHAR(length=32), nullable=False),
    sa.Column('id_pedido', sa.VARCHAR(length=32), nullable=False),
    sa.Column('avaliacao', sa.INTEGER(), nullable=False),
    sa.Column('titulo_comentario', sa.VARCHAR(length=255), nullable=True),
    sa.Column('comentario', sa.VARCHAR(length=1000), nullable=True),
    sa.Column('data_comentario', sa.DATETIME(), nullable=True),
    sa.Column('data_resposta', sa.DATETIME(), nullable=True),
    sa.Column('resposta_admin', sa.TEXT(), nullable=True),
    sa.Column('autor_resposta', sa.VARCHAR(length=255), nullable=True),
    sa.ForeignKeyConstraint(['id_pedido'], ['pedidos.id_pedido'], ),
    sa.PrimaryKeyConstraint('id_avaliacao')
    )
    op.create_index('ix_avaliacoes_pedidos_id_pedido', 'avaliacoes_pedidos', ['id_pedido'], unique=False)
    op.create_table('consumidores',
    sa.Column('id_consumidor', sa.VARCHAR(length=32), nullable=False),
    sa.Column('prefixo_cep', sa.VARCHAR(length=10), nullable=False),
    sa.Column('nome_consumidor', sa.VARCHAR(length=255), nullable=False),
    sa.Column('cidade', sa.VARCHAR(length=100), nullable=False),
    sa.Column('estado', sa.VARCHAR(length=2), nullable=False),
    sa.PrimaryKeyConstraint('id_consumidor')
    )
    # ### end Alembic commands ###
