"""Schemas Pydantic de request e response da aplicação."""

from app.schemas.produto import (
    AvaliacaoStats,
    ItemAvaliacao,
    PaginatedProdutos,
    ProdutoCreate,
    ProdutoDetalhe,
    ProdutoListItem,
    ProdutoUpdate,
    VendaStats,
)

__all__ = [
    "AvaliacaoStats",
    "ItemAvaliacao",
    "PaginatedProdutos",
    "ProdutoCreate",
    "ProdutoDetalhe",
    "ProdutoListItem",
    "ProdutoUpdate",
    "VendaStats",
]
