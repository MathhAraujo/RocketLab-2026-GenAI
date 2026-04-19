"""Orchestrator service for the /api/assistente/perguntar endpoint.

Coordinates SQL agent, guardrail validation, read-only DB execution, PII
anonymisation, and response composition. Zero FastAPI imports — all HTTP
concerns live in the router layer.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Final, Literal, TypeAlias

from sqlalchemy import Engine, text

import app.agents.insight_agent as _insight_mod
import app.agents.sql_agent as _sql_mod
from app.agents.sql_agent import SqlGenerationResult
from app.errors import GeminiNotConfiguredError, GeminiQuotaExhaustedError, GeminiRateLimitError
from app.schemas.assistente import (
    GraficoVisualizacao,
    MetadadosResposta,
    RespostaAssistente,
    TabelaVisualizacao,
    Visualizacao,
)
from app.services.anonymizer import anonymize_rows
from app.services.retry import MAX_ATTEMPTS, RetryContext
from app.services.sql_guardrail import QueryNotAllowedError, validate_and_harden

logger = logging.getLogger(__name__)

_QUERY_TIMEOUT: Final[float] = 30.0
_INSIGHT_MIN_ROWS: Final[int] = 3
_INSIGHT_MAX_ROWS: Final[int] = 100
_VALID_CHART_TYPES: Final[frozenset[str]] = frozenset({"bar", "line", "pie", "area", "scatter"})
_FALLBACK_MESSAGE: Final[str] = (
    "Não consegui responder sua pergunta. Tente reformular, "
    "por exemplo especificando períodos, estados ou categorias."
)

_ChartSubtype: TypeAlias = Literal["bar", "line", "pie", "area", "scatter"]


def _run_sync_query(sql: str, engine: Engine) -> tuple[list[str], list[list[Any]]]:
    with engine.connect() as conn:
        result = conn.execute(text(sql))
        columns = list(result.keys())
        rows = [list(row) for row in result]
    return columns, rows


async def _executar_consulta(
    sql: str,
    engine: Engine,
) -> tuple[list[str], list[list[Any]]]:
    """Execute *sql* on *engine* inside a thread pool with a hard timeout."""
    loop = asyncio.get_running_loop()
    future = loop.run_in_executor(None, lambda: _run_sync_query(sql, engine))
    return await asyncio.wait_for(future, timeout=_QUERY_TIMEOUT)


def _tem_coluna_numerica(rows: list[list[Any]]) -> bool:
    if not rows:
        return False
    return any(isinstance(v, int | float) for v in rows[0])


def _deve_chamar_insight(rows: list[list[Any]]) -> bool:
    return _INSIGHT_MIN_ROWS <= len(rows) <= _INSIGHT_MAX_ROWS and _tem_coluna_numerica(rows)


def _parse_chart_subtype(value: str) -> _ChartSubtype | None:
    if value in _VALID_CHART_TYPES:
        return value  # type: ignore[return-value]  # validated by set membership
    return None


def _construir_grafico(
    sql_result: SqlGenerationResult,
    columns: list[str],
    rows: list[list[Any]],
) -> GraficoVisualizacao | None:
    """Return a GraficoVisualizacao if the agent suggested a valid chart type."""
    subtype = _parse_chart_subtype(sql_result.sugestao_grafico)
    if subtype is None:
        return None
    config = sql_result.grafico_config
    eixo_x = config.eixo_x if config and config.eixo_x else (columns[0] if columns else "")
    eixo_y = config.eixo_y if config and config.eixo_y else (columns[1] if len(columns) > 1 else "")
    titulo = sql_result.explicacao_seca[:80] or "Resultado"
    dados: list[dict[str, Any]] = [dict(zip(columns, row, strict=True)) for row in rows]
    return GraficoVisualizacao(
        subtipo=subtype,
        titulo=titulo,
        eixo_x=eixo_x,
        eixo_y=eixo_y,
        dados=dados,
    )


def _construir_visualizacoes(
    sql_result: SqlGenerationResult,
    columns: list[str],
    rows: list[list[Any]],
) -> list[Visualizacao]:
    """Compose visualisation blocks following §7.2 composition rules."""
    visualizacoes: list[Visualizacao] = []
    titulo = sql_result.explicacao_seca[:80] or "Resultado"

    if sql_result.forcar_tabela:
        visualizacoes.append(TabelaVisualizacao(titulo=titulo, colunas=columns, linhas=rows))

    grafico = _construir_grafico(sql_result, columns, rows)
    if grafico is not None:
        visualizacoes.append(grafico)

    if not visualizacoes:
        visualizacoes.append(TabelaVisualizacao(titulo=titulo, colunas=columns, linhas=rows))

    return visualizacoes


def _resposta_off_topic(
    pergunta: str,
    sql_result: SqlGenerationResult,
    anonimizar: bool,
) -> RespostaAssistente:
    mensagem = sql_result.mensagem_off_topic or (
        "Esta ferramenta responde apenas perguntas sobre os dados do e-commerce. "
        "Exemplos: 'Top 10 produtos mais vendidos', 'Pedidos por status'."
    )
    return RespostaAssistente(
        pergunta=pergunta,
        visualizacoes=[],
        tentativas=1,
        erro_amigavel=mensagem,
        metadados=MetadadosResposta(motivo="off_topic", anonimizado=anonimizar),
    )


def _resposta_fallback(
    pergunta: str,
    anonimizar: bool,
    tentativas: int,
) -> RespostaAssistente:
    return RespostaAssistente(
        pergunta=pergunta,
        visualizacoes=[],
        tentativas=tentativas,
        erro_amigavel=_FALLBACK_MESSAGE,
        metadados=MetadadosResposta(anonimizado=anonimizar),
    )


async def _compor_resposta(
    pergunta: str,
    sql_result: SqlGenerationResult,
    columns: list[str],
    rows: list[list[Any]],
    anonimizar: bool,
    tentativas: int,
) -> RespostaAssistente:
    """Build the full RespostaAssistente, running the insight agent when applicable."""
    explicacao: str | None = sql_result.explicacao_seca or None
    usou_insight = False

    if _deve_chamar_insight(rows):
        try:
            insight = await _insight_mod.gerar_insight(
                pergunta, columns, rows[:_INSIGHT_MAX_ROWS], sql_result.explicacao_seca
            )
            explicacao = insight.explicacao_analitica
            usou_insight = True
        except Exception as exc:
            logger.warning("Insight agent falhou; usando explicação seca: %s", exc)

    return RespostaAssistente(
        pergunta=pergunta,
        sql_gerado=sql_result.sql or None,
        explicacao=explicacao,
        visualizacoes=_construir_visualizacoes(sql_result, columns, rows),
        tentativas=tentativas,
        metadados=MetadadosResposta(
            anonimizado=anonimizar,
            linhas_retornadas=len(rows),
            usou_insight=usou_insight,
        ),
    )


async def responder_pergunta(
    pergunta: str,
    anonimizar: bool,
    engine: Engine,
) -> RespostaAssistente:
    """Orchestrate the full Text-to-SQL pipeline for a user question.

    Calls the SQL agent up to ``MAX_ATTEMPTS`` times on transient failures,
    validates the generated query, executes it on *engine*, optionally
    anonymises PII rows, and composes the structured response.

    Args:
        pergunta: The user's question in pt-BR.
        anonimizar: Whether to mask PII fields in the result.
        engine: Read-only SQLAlchemy engine for query execution.

    Returns:
        A ``RespostaAssistente`` with data, visualisations, and metadata.
        Falls back to a friendly 200 response after all retries are exhausted
        (unless the failure is a hard security or configuration error).

    Raises:
        QueryNotAllowedError: Re-raised when the agent generates forbidden SQL
            on every attempt (security violation, not a transient error).
        GeminiNotConfiguredError: Re-raised immediately when the AI service
            is not configured — no retry makes sense.
    """
    context: RetryContext | None = None
    last_exc: Exception | None = None
    sql_attempted: str | None = None

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            sql_result = await _sql_mod.gerar_sql(pergunta, context)
            if sql_result.eh_off_topic:
                return _resposta_off_topic(pergunta, sql_result, anonimizar)

            sql_attempted = sql_result.sql
            hardened = validate_and_harden(sql_result.sql)
            columns, rows = await _executar_consulta(hardened, engine)
            rows = anonymize_rows(columns, rows, enabled=anonimizar)
            return await _compor_resposta(pergunta, sql_result, columns, rows, anonimizar, attempt)
        except (GeminiNotConfiguredError, GeminiRateLimitError, GeminiQuotaExhaustedError):
            raise
        except Exception as exc:
            logger.warning("Tentativa %d/%d falhou: %s", attempt, MAX_ATTEMPTS, exc)
            context = RetryContext(sql_anterior=sql_attempted, mensagem_erro=str(exc))
            sql_attempted = None
            last_exc = exc

    logger.error("Esgotadas %d tentativas para: %r", MAX_ATTEMPTS, pergunta)
    if isinstance(last_exc, QueryNotAllowedError):
        raise last_exc
    return _resposta_fallback(pergunta, anonimizar, MAX_ATTEMPTS)
