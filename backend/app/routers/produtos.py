"""Router FastAPI para CRUD de produtos, vendas e avaliações."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from math import ceil
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, require_admin
from app.models.avaliacao_pedido import AvaliacaoPedido
from app.models.item_pedido import ItemPedido
from app.models.pedido import Pedido
from app.models.produto import Produto
from app.models.usuario import Usuario
from app.schemas.produto import (
    AvaliacaoStats,
    ItemAvaliacao,
    PaginatedProdutos,
    ProdutoCreate,
    ProdutoDetalhe,
    ProdutoListItem,
    ProdutoUpdate,
    RespostaRequest,
    VendaStats,
)

router = APIRouter(prefix="/produtos", tags=["Produtos"])


def _buscar_produto(id_produto: str, db: Session) -> dict[str, Any] | None:
    """Buscar produto por ID e retornar seus campos como dicionário ou None se inexistente."""
    p = db.query(Produto).filter(Produto.id_produto == id_produto).first()
    if not p:
        return None
    return {c.name: getattr(p, c.name) for c in p.__table__.columns}


_ORDENACAO: dict[str, list[Any]] = {
    "nome_produto": [Produto.nome_produto],
    "categoria_produto": [Produto.categoria_produto],
    "preco_medio": [Produto.preco_medio],
    "avaliacao_media": [Produto.avaliacao_media, Produto.total_avaliacoes],
    "avaliacoes": [Produto.avaliacao_media, Produto.total_avaliacoes],
    "total_vendas": [Produto.total_vendas],
    "vendas": [Produto.total_vendas],
}


@router.get(
    "/",
    response_model=PaginatedProdutos,
    summary="Listar Produtos",
    description=(
        "Lista paginada de produtos com opções de busca, filtro por categoria "
        "e cálculo de totais de venda e avaliação média."
    ),
)
@cache(expire=60)  # type: ignore[arg-type]
def listar_produtos(
    busca: str | None = Query(None, alias="search"),
    categoria: str | None = Query(None),
    pagina: int = Query(1, alias="page", ge=1),
    por_pagina: int = Query(20, alias="per_page", ge=1, le=100),
    ordenar_por: str = Query("nome_produto", alias="sort_by"),
    ordem: str = Query("asc", alias="order"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> dict[str, Any]:
    """Listar produtos com paginação, busca textual e ordenação."""
    query = db.query(Produto)

    if busca:
        termo = f"%{busca}%"
        query = query.filter(
            Produto.nome_produto.ilike(termo) | Produto.categoria_produto.ilike(termo)
        )
    if categoria:
        query = query.filter(Produto.categoria_produto == categoria)

    total = query.count()

    colunas = _ORDENACAO.get(ordenar_por, _ORDENACAO["nome_produto"])
    colunas_ordenadas = [coluna.desc() if ordem == "desc" else coluna.asc() for coluna in colunas]

    skip = (pagina - 1) * por_pagina
    linhas = query.order_by(*colunas_ordenadas).offset(skip).limit(por_pagina).all()

    return {
        "items": [
            ProdutoListItem(**{c.name: getattr(linha, c.name) for c in linha.__table__.columns})
            for linha in linhas
        ],
        "total": total,
        "page": pagina,
        "per_page": por_pagina,
        "pages": ceil(total / por_pagina) if total > 0 else 0,
    }


@router.get(
    "/categorias",
    response_model=list[str],
    summary="Listar Categorias",
    description="Retorna todas as categorias únicas de produtos registradas.",
)
@cache(expire=60)  # type: ignore[arg-type]
def listar_categorias(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> list[str]:
    """Retornar lista ordenada de categorias únicas de produtos."""
    rows = db.query(Produto.categoria_produto).distinct().order_by(Produto.categoria_produto).all()
    return [r[0] for r in rows]


@router.get(
    "/{id_produto}",
    response_model=ProdutoDetalhe,
    summary="Obter Produto",
    description="Retorna detalhes completos de um produto específico com base no seu ID.",
)
@cache(expire=60)  # type: ignore[arg-type]
def obter_produto(
    id_produto: str,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> dict[str, Any]:
    """Retornar detalhes completos de um produto ou 404 se não encontrado."""
    produto = _buscar_produto(id_produto, db)
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return produto


@router.post(
    "/",
    response_model=ProdutoDetalhe,
    status_code=201,
    summary="Criar Produto",
    description="Registra um novo produto.",
)
async def criar_produto(
    payload: ProdutoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin),
) -> dict[str, Any]:
    """Criar produto e invalidar o cache de listagem."""
    novo = Produto(id_produto=uuid.uuid4().hex, **payload.model_dump())
    db.add(novo)
    db.commit()
    await FastAPICache.get_backend().clear()
    result = _buscar_produto(novo.id_produto, db)
    if result is None:
        raise HTTPException(status_code=500, detail="Erro ao recuperar produto criado.")
    return result


@router.put(
    "/{id_produto}",
    response_model=ProdutoDetalhe,
    summary="Atualizar Produto",
    description="Altera as propriedades de um produto existente com base em seu ID.",
)
async def atualizar_produto(
    id_produto: str,
    payload: ProdutoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin),
) -> dict[str, Any]:
    """Atualizar campos do produto e invalidar o cache."""
    campos = payload.model_dump(exclude_unset=True)
    if not campos:
        raise HTTPException(status_code=422, detail="Nenhum campo para atualizar")

    produto = db.query(Produto).filter(Produto.id_produto == id_produto).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    for campo, valor in campos.items():
        setattr(produto, campo, valor)
    db.commit()
    await FastAPICache.get_backend().clear()
    result = _buscar_produto(id_produto, db)
    if result is None:
        raise HTTPException(status_code=500, detail="Erro ao recuperar produto atualizado.")
    return result


@router.delete(
    "/{id_produto}",
    status_code=204,
    summary="Deletar Produto",
    description="Deleta um produto de forma definitiva.",
)
async def deletar_produto(
    id_produto: str,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin),
) -> None:
    """Remover produto do banco e invalidar o cache."""
    produto = db.query(Produto).filter(Produto.id_produto == id_produto).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    db.delete(produto)
    db.commit()
    await FastAPICache.get_backend().clear()


@router.get(
    "/{id_produto}/vendas",
    response_model=VendaStats,
    summary="Obter Vendas do Produto",
    description="Calcula e retorna estatísticas consolidadas de venda de um produto.",
)
@cache(expire=60)  # type: ignore[arg-type]
def obter_vendas_produto(
    id_produto: str,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> VendaStats:
    """Calcular estatísticas de vendas de um produto a partir dos itens de pedido."""
    if not db.query(Produto).filter(Produto.id_produto == id_produto).first():
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    stats = (
        db.query(
            func.count(ItemPedido.id_item).label("total_vendas"),
            func.coalesce(func.sum(ItemPedido.preco_BRL), 0.0).label("receita_total"),
            func.avg(ItemPedido.preco_BRL).label("preco_medio"),
            func.min(ItemPedido.preco_BRL).label("preco_minimo"),
            func.max(ItemPedido.preco_BRL).label("preco_maximo"),
            func.count(func.distinct(ItemPedido.id_pedido)).label("total_pedidos"),
        )
        .filter(ItemPedido.id_produto == id_produto)
        .one()
    )

    status_rows = (
        db.query(Pedido.status, func.count(Pedido.id_pedido).label("qtd"))
        .join(ItemPedido, ItemPedido.id_pedido == Pedido.id_pedido)
        .filter(ItemPedido.id_produto == id_produto)
        .group_by(Pedido.status)
        .all()
    )

    return VendaStats(
        total_vendas=stats.total_vendas,
        receita_total=float(stats.receita_total),
        preco_medio=float(stats.preco_medio) if stats.preco_medio is not None else None,
        preco_minimo=float(stats.preco_minimo) if stats.preco_minimo is not None else None,
        preco_maximo=float(stats.preco_maximo) if stats.preco_maximo is not None else None,
        total_pedidos=stats.total_pedidos,
        vendas_por_status={row.status: row.qtd for row in status_rows},
    )


@router.get(
    "/{id_produto}/avaliacoes",
    response_model=AvaliacaoStats,
    summary="Listar Avaliações do Produto",
    description=(
        "Recupera de maneira paginada as avaliações de consumidores atreladas a este produto."
    ),
)
@cache(expire=60)  # type: ignore[arg-type]
def listar_avaliacoes_produto(
    id_produto: str,
    pagina: int = Query(1, alias="page", ge=1),
    por_pagina: int = Query(10, alias="per_page", ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> AvaliacaoStats:
    """Retornar estatísticas e listagem paginada de avaliações de um produto."""
    if not db.query(Produto).filter(Produto.id_produto == id_produto).first():
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    sq_pedidos = (
        db.query(ItemPedido.id_pedido).filter(ItemPedido.id_produto == id_produto).distinct()
    )

    query_base = db.query(AvaliacaoPedido).filter(AvaliacaoPedido.id_pedido.in_(sq_pedidos))

    total = query_base.count()

    stats = (
        db.query(
            func.avg(AvaliacaoPedido.avaliacao).label("avaliacao_media"),
            func.count(AvaliacaoPedido.id_avaliacao).label("total_avaliacoes"),
        )
        .filter(AvaliacaoPedido.id_pedido.in_(sq_pedidos))
        .one()
    )

    dist_rows = (
        db.query(AvaliacaoPedido.avaliacao, func.count().label("qtd"))
        .filter(AvaliacaoPedido.id_pedido.in_(sq_pedidos))
        .group_by(AvaliacaoPedido.avaliacao)
        .all()
    )

    skip = (pagina - 1) * por_pagina
    avaliacoes = (
        query_base.order_by(AvaliacaoPedido.data_comentario.desc())
        .offset(skip)
        .limit(por_pagina)
        .all()
    )

    return AvaliacaoStats(
        avaliacao_media=(
            float(stats.avaliacao_media) if stats.avaliacao_media is not None else None
        ),
        total_avaliacoes=stats.total_avaliacoes,
        distribuicao={row.avaliacao: row.qtd for row in dist_rows},
        avaliacoes=[
            ItemAvaliacao(
                id_avaliacao=av.id_avaliacao,
                avaliacao=av.avaliacao,
                titulo_comentario=av.titulo_comentario,
                comentario=av.comentario,
                data_comentario=(av.data_comentario.isoformat() if av.data_comentario else None),
                resposta_admin=av.resposta_admin,
                autor_resposta=av.autor_resposta,
                data_resposta=(av.data_resposta.isoformat() if av.data_resposta else None),
            )
            for av in avaliacoes
        ],
        total=total,
        page=pagina,
        per_page=por_pagina,
        pages=ceil(total / por_pagina) if total > 0 else 0,
    )


@router.post(
    "/avaliacoes/{id_avaliacao}/resposta",
    response_model=ItemAvaliacao,
    summary="Responder Avaliação",
    description="Permite que um administrador publique uma resposta à avaliação de um consumidor.",
    responses={
        404: {"description": "Avaliação não encontrada."},
        403: {"description": "Privilégios insuficientes para realizar esta ação."},
    },
)
async def responder_avaliacao(
    id_avaliacao: str,
    payload: RespostaRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin),
) -> ItemAvaliacao:
    """Publicar resposta do admin a uma avaliação e invalidar o cache."""
    av = db.query(AvaliacaoPedido).filter(AvaliacaoPedido.id_avaliacao == id_avaliacao).first()
    if not av:
        raise HTTPException(status_code=404, detail="Avaliação não encontrada")
    av.resposta_admin = payload.resposta
    av.autor_resposta = current_user.username
    av.data_resposta = datetime.now(UTC)
    db.commit()
    db.refresh(av)
    await FastAPICache.get_backend().clear()
    return ItemAvaliacao(
        id_avaliacao=av.id_avaliacao,
        avaliacao=av.avaliacao,
        titulo_comentario=av.titulo_comentario,
        comentario=av.comentario,
        data_comentario=av.data_comentario.isoformat() if av.data_comentario else None,
        resposta_admin=av.resposta_admin,
        autor_resposta=av.autor_resposta,
        data_resposta=av.data_resposta.isoformat() if av.data_resposta else None,
    )


@router.delete(
    "/avaliacoes/{id_avaliacao}/resposta",
    response_model=ItemAvaliacao,
    summary="Deletar Resposta da Avaliação",
    description="Permite que um administrador exclua uma resposta publicada em uma avaliação.",
    responses={
        404: {"description": "Avaliação não encontrada."},
        403: {"description": "Privilégios insuficientes para realizar esta ação."},
    },
)
async def deletar_resposta_avaliacao(
    id_avaliacao: str,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin),
) -> ItemAvaliacao:
    """Remover resposta do admin de uma avaliação e invalidar o cache."""
    av = db.query(AvaliacaoPedido).filter(AvaliacaoPedido.id_avaliacao == id_avaliacao).first()
    if not av:
        raise HTTPException(status_code=404, detail="Avaliação não encontrada")
    av.resposta_admin = None
    av.autor_resposta = None
    av.data_resposta = None
    db.commit()
    db.refresh(av)
    await FastAPICache.get_backend().clear()
    return ItemAvaliacao(
        id_avaliacao=av.id_avaliacao,
        avaliacao=av.avaliacao,
        titulo_comentario=av.titulo_comentario,
        comentario=av.comentario,
        data_comentario=av.data_comentario.isoformat() if av.data_comentario else None,
        resposta_admin=av.resposta_admin,
        autor_resposta=av.autor_resposta,
        data_resposta=av.data_resposta.isoformat() if av.data_resposta else None,
    )
