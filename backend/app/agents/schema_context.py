"""Database schema constant injected into agent system prompts.

``SCHEMA_BLOCK`` is a formatted string describing every table available to
the SQL agent.  It is embedded verbatim inside the system prompt so the
model knows the exact column names, types and relationships without any
runtime introspection of the database.
"""

from __future__ import annotations

from typing import Final

SCHEMA_BLOCK: Final[str] = """
## Tabelas disponíveis

### consumidores — clientes finais
- id_consumidor (String 32, PK)
- prefixo_cep (String 10)
- nome_consumidor (String 255) 🔒 PII
- cidade (String 100)
- estado (String 2)

### vendedores — vendedores cadastrados
- id_vendedor (String 32, PK)
- nome_vendedor (String 255) 🔒 PII
- prefixo_cep (String 10)
- cidade (String 100)
- estado (String 2)

### produtos — catálogo (contém colunas desnormalizadas/agregadas)
- id_produto (String 32, PK)
- nome_produto (String 255)
- categoria_produto (String 100)
- peso_produto_gramas (Float, nullable)
- comprimento_centimetros (Float, nullable)
- altura_centimetros (Float, nullable)
- largura_centimetros (Float, nullable)
- total_vendas (Integer, default 0, not null) — agregado
- preco_medio (Float, nullable) — agregado
- total_avaliacoes (Integer, default 0, not null) — agregado
- avaliacao_media (Float, nullable) — agregado

### pedidos — cabeçalho dos pedidos
- id_pedido (String 32, PK)
- id_consumidor (String 32, FK → consumidores.id_consumidor, not null)
- status (String 50)
- pedido_compra_timestamp (DateTime, nullable)
- pedido_entregue_timestamp (DateTime, nullable)
- data_estimada_entrega (Date, nullable)
- tempo_entrega_dias (Float, nullable)
- tempo_entrega_estimado_dias (Float, nullable)
- diferenca_entrega_dias (Float, nullable) — positivo = atraso
- entrega_no_prazo (String 10, nullable) — NÃO é boolean; use = 'sim' / = 'nao'

### itens_pedidos — itens de cada pedido
- id_pedido (String 32, FK → pedidos.id_pedido, not null) — PK composta com id_item
- id_item (Integer, not null) — PK composta com id_pedido
- id_produto (String 32, FK → produtos.id_produto, not null, indexado)
- id_vendedor (String 32, FK → vendedores.id_vendedor, not null)
- preco_BRL (Float)
- preco_frete (Float)

### avaliacoes_pedidos — reviews de pedidos
- id_avaliacao (String 32, PK)
- id_pedido (String 32, FK → pedidos.id_pedido, not null, indexado)
- avaliacao (Integer) — escala 1-5
- titulo_comentario (String 255, nullable) 🔒 PII potencial
- comentario (String 1000, nullable) 🔒 PII potencial
- data_comentario (DateTime, nullable)
- data_resposta (DateTime, nullable)
- resposta_admin (Text, nullable)
- autor_resposta (String 255, nullable)

### usuarios — ⛔ BLOQUEADA (contém hashed_password; NUNCA consulte esta tabela)
- id_usuario (String 32, PK)
- username (String 255, único)
- hashed_password (String 255)
- is_admin (Boolean)

## Observações de modelagem

- Receita total de um pedido: SUM(preco_BRL + preco_frete) em itens_pedidos agrupado por id_pedido.
- Receita por categoria: JOIN itens_pedidos → produtos, GROUP BY categoria_produto.
- Receita por estado: JOIN itens_pedidos → pedidos → consumidores, GROUP BY estado.
- Colunas agregadas em produtos (total_vendas, preco_medio etc.) são atalhos; prefira JOINs a partir
  das tabelas de fato quando precisar de dados atualizados ou filtrados.
- pedidos.entrega_no_prazo é String(10) — use = 'sim' ou = 'nao', NUNCA = TRUE / = FALSE.
""".strip()
