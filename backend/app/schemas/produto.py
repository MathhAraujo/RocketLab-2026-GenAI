"""Schemas Pydantic para CRUD de produtos, vendas e avaliações."""

from __future__ import annotations

from pydantic import BaseModel


class ProdutoBase(BaseModel):
    """Campos compartilhados entre criação e atualização de produto."""

    nome_produto: str
    categoria_produto: str
    peso_produto_gramas: float | None = None
    comprimento_centimetros: float | None = None
    altura_centimetros: float | None = None
    largura_centimetros: float | None = None


class ProdutoCreate(ProdutoBase):
    """Payload para criação de um novo produto."""


class ProdutoUpdate(BaseModel):
    """Payload de atualização parcial de produto — todos os campos são opcionais."""

    nome_produto: str | None = None
    categoria_produto: str | None = None
    peso_produto_gramas: float | None = None
    comprimento_centimetros: float | None = None
    altura_centimetros: float | None = None
    largura_centimetros: float | None = None


class ProdutoListItem(BaseModel):
    """Representação resumida de produto usada na listagem paginada."""

    id_produto: str
    nome_produto: str
    categoria_produto: str
    preco_medio: float | None = None
    avaliacao_media: float | None = None
    total_avaliacoes: int = 0
    total_vendas: int = 0

    model_config = {"from_attributes": True}


class ProdutoDetalhe(ProdutoListItem):
    """Representação completa de produto com dimensões físicas."""

    peso_produto_gramas: float | None = None
    comprimento_centimetros: float | None = None
    altura_centimetros: float | None = None
    largura_centimetros: float | None = None


class PaginatedProdutos(BaseModel):
    """Resposta paginada da listagem de produtos."""

    items: list[ProdutoListItem]
    total: int
    page: int
    per_page: int
    pages: int


class VendaStats(BaseModel):
    """Estatísticas consolidadas de vendas de um produto."""

    total_vendas: int
    receita_total: float
    preco_medio: float | None = None
    preco_minimo: float | None = None
    preco_maximo: float | None = None
    total_pedidos: int
    vendas_por_status: dict[str, int]


class ItemAvaliacao(BaseModel):
    """Avaliação individual de consumidor com resposta do administrador."""

    id_avaliacao: str
    avaliacao: int
    titulo_comentario: str | None = None
    comentario: str | None = None
    data_comentario: str | None = None
    resposta_admin: str | None = None
    autor_resposta: str | None = None
    data_resposta: str | None = None


class AvaliacaoStats(BaseModel):
    """Estatísticas e listagem paginada de avaliações de um produto."""

    avaliacao_media: float | None = None
    total_avaliacoes: int
    distribuicao: dict[int, int]
    avaliacoes: list[ItemAvaliacao]
    total: int
    page: int
    per_page: int
    pages: int


class RespostaRequest(BaseModel):
    """Payload para publicar ou atualizar a resposta do admin a uma avaliação."""

    resposta: str
