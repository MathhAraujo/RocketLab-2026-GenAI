"""Unit tests for sql_agent and insight_agent without real Gemini API calls.

All external agent.run calls are replaced with AsyncMock so no network
requests are made. Tests follow the AAA pattern.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from pydantic_ai.exceptions import ModelHTTPError

import app.agents.insight_agent as insight_mod
import app.agents.sql_agent as sql_mod
from app.agents.insight_agent import InsightResult
from app.agents.sql_agent import SqlGenerationResult
from app.agents.sql_agent import _build_prompt as sql_build_prompt
from app.errors import GeminiNotConfiguredError, GeminiQuotaExhaustedError, GeminiRateLimitError
from app.services.retry import RetryContext

pytestmark = pytest.mark.anyio

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_CANNED_SQL = "SELECT nome_produto FROM produtos LIMIT 10"


def _sql_result(**kwargs) -> SqlGenerationResult:  # type: ignore[no-untyped-def]
    defaults = {
        "sql": _CANNED_SQL,
        "explicacao_seca": "Teste.",
        "sugestao_grafico": "none",
        "grafico_config": None,
        "forcar_tabela": True,
        "eh_off_topic": False,
    }
    defaults.update(kwargs)
    return SqlGenerationResult(**defaults)


def _patch_run(monkeypatch: pytest.MonkeyPatch, module: object, output: object) -> AsyncMock:
    run = AsyncMock(return_value=MagicMock(output=output))
    monkeypatch.setattr(module, "_agent", MagicMock(run=run))  # type: ignore[arg-type]
    return run


# ---------------------------------------------------------------------------
# sql_agent — _build_prompt (pure function, no async)
# ---------------------------------------------------------------------------


def test_sql_build_prompt_without_context_returns_question() -> None:
    assert sql_build_prompt("Top 10 produtos", None) == "Top 10 produtos"


def test_sql_build_prompt_with_context_appends_error_info() -> None:
    ctx = RetryContext(sql_anterior="SELECT * FROM usuarios", mensagem_erro="Tabela bloqueada")

    result = sql_build_prompt("Top 10 produtos", ctx)

    assert "Top 10 produtos" in result
    assert "SELECT * FROM usuarios" in result
    assert "Tabela bloqueada" in result


# ---------------------------------------------------------------------------
# sql_agent — gerar_sql
# ---------------------------------------------------------------------------


async def test_gerar_sql_raises_when_no_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sql_mod.settings, "GOOGLE_API_KEY", None)

    with pytest.raises(GeminiNotConfiguredError):
        await sql_mod.gerar_sql("Top 10 produtos")


async def test_gerar_sql_returns_result_when_api_key_set(monkeypatch: pytest.MonkeyPatch) -> None:
    expected = _sql_result(sql=_CANNED_SQL)
    _patch_run(monkeypatch, sql_mod, expected)
    monkeypatch.setattr(sql_mod.settings, "GOOGLE_API_KEY", "fake-key")

    result = await sql_mod.gerar_sql("Top 10 produtos")

    assert result.sql == _CANNED_SQL


async def test_gerar_sql_with_retry_context_passes_context_to_prompt(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    run_mock = _patch_run(monkeypatch, sql_mod, _sql_result())
    monkeypatch.setattr(sql_mod.settings, "GOOGLE_API_KEY", "fake-key")
    ctx = RetryContext(sql_anterior="SELECT bad", mensagem_erro="syntax error")

    await sql_mod.gerar_sql("Pedidos recentes", retry_context=ctx)

    prompt: str = str(run_mock.call_args.args[0])
    assert "SELECT bad" in prompt
    assert "syntax error" in prompt


# ---------------------------------------------------------------------------
# insight_agent — gerar_insight
# ---------------------------------------------------------------------------


async def test_gerar_insight_returns_analytic_result(monkeypatch: pytest.MonkeyPatch) -> None:
    expected = InsightResult(explicacao_analitica="Produto A lidera com 100 vendas.")
    _patch_run(monkeypatch, insight_mod, expected)

    result = await insight_mod.gerar_insight(
        pergunta="Top produtos",
        colunas=["produto", "vendas"],
        linhas_top100=[["A", 100], ["B", 50]],
        explicacao_seca="Os 2 produtos mais vendidos.",
    )

    assert "Produto A" in result.explicacao_analitica


async def test_gerar_sql_raises_rate_limit_on_http_429(monkeypatch: pytest.MonkeyPatch) -> None:
    # Arrange
    exc = ModelHTTPError(status_code=429, model_name="gemini-2.5-flash")
    monkeypatch.setattr(sql_mod, "_agent", MagicMock(run=AsyncMock(side_effect=exc)))
    monkeypatch.setattr(sql_mod.settings, "GOOGLE_API_KEY", "fake-key")
    # Act / Assert
    with pytest.raises(GeminiRateLimitError):
        await sql_mod.gerar_sql("Top 10 produtos")


async def test_gerar_sql_raises_quota_exhausted_on_429_with_quota_body(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Arrange
    exc = ModelHTTPError(status_code=429, model_name="gemini-2.5-flash", body="quota exceeded")
    monkeypatch.setattr(sql_mod, "_agent", MagicMock(run=AsyncMock(side_effect=exc)))
    monkeypatch.setattr(sql_mod.settings, "GOOGLE_API_KEY", "fake-key")
    # Act / Assert
    with pytest.raises(GeminiQuotaExhaustedError):
        await sql_mod.gerar_sql("Top 10 produtos")


async def test_gerar_insight_prompt_includes_question_and_columns(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    run_mock = _patch_run(monkeypatch, insight_mod, InsightResult(explicacao_analitica="Análise."))

    await insight_mod.gerar_insight(
        pergunta="Minha pergunta",
        colunas=["col_a", "col_b"],
        linhas_top100=[["x", 1]],
        explicacao_seca="Explicação seca.",
    )

    prompt: str = str(run_mock.call_args.args[0])
    assert "Minha pergunta" in prompt
    assert "col_a" in prompt
