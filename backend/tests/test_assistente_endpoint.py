"""Integration tests for POST /api/assistente/perguntar and GET /api/assistente/saude.

All tests use mocked agents (no real Gemini calls).  State is RED until
TASK-16, TASK-17 and TASK-18 provide the service, router and registration.
"""

from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.agents.insight_agent import InsightResult
from app.agents.sql_agent import SqlGenerationResult

_URL = "/api/assistente/perguntar"
_HEALTH_URL = "/api/assistente/saude"
_PERGUNTA = "Top 10 produtos mais vendidos"


# ---------------------------------------------------------------------------
# Auth / access control
# ---------------------------------------------------------------------------


def test_unauthenticated_returns_401(admin_client: TestClient) -> None:
    # Arrange / Act
    r = admin_client.post(_URL, json={"pergunta": _PERGUNTA})
    # Assert
    assert r.status_code == 401


def test_viewer_returns_403(
    viewer_client: TestClient,
    viewer_token: str,
) -> None:
    # Arrange
    headers = {"Authorization": f"Bearer {viewer_token}"}
    # Act
    r = viewer_client.post(_URL, json={"pergunta": _PERGUNTA}, headers=headers)
    # Assert
    assert r.status_code == 403


# ---------------------------------------------------------------------------
# Happy-path contract
# ---------------------------------------------------------------------------


def test_admin_can_post_valid_question(
    admin_client: TestClient,
    admin_token: str,
    mock_sql_agent: SqlGenerationResult,
    mock_insight_agent: InsightResult,
) -> None:
    headers = {"Authorization": f"Bearer {admin_token}"}
    r = admin_client.post(_URL, json={"pergunta": _PERGUNTA}, headers=headers)
    assert r.status_code == 200


def test_response_shape_matches_contract(
    admin_client: TestClient,
    admin_token: str,
    mock_sql_agent: SqlGenerationResult,
    mock_insight_agent: InsightResult,
) -> None:
    headers = {"Authorization": f"Bearer {admin_token}"}
    r = admin_client.post(_URL, json={"pergunta": _PERGUNTA}, headers=headers)
    body = r.json()
    assert "pergunta" in body
    assert "visualizacoes" in body
    assert "metadados" in body


def test_sql_gerado_is_returned(
    admin_client: TestClient,
    admin_token: str,
    mock_sql_agent: SqlGenerationResult,
    mock_insight_agent: InsightResult,
) -> None:
    headers = {"Authorization": f"Bearer {admin_token}"}
    r = admin_client.post(_URL, json={"pergunta": _PERGUNTA}, headers=headers)
    assert r.json()["sql_gerado"] is not None


def test_visualizacoes_contains_tabela_by_default(
    admin_client: TestClient,
    admin_token: str,
    mock_sql_agent: SqlGenerationResult,
    mock_insight_agent: InsightResult,
) -> None:
    headers = {"Authorization": f"Bearer {admin_token}"}
    r = admin_client.post(_URL, json={"pergunta": _PERGUNTA}, headers=headers)
    tipos = [v["tipo"] for v in r.json()["visualizacoes"]]
    assert "tabela" in tipos


def test_grafico_included_when_agent_suggests(
    admin_client: TestClient,
    admin_token: str,
    mock_sql_agent: SqlGenerationResult,
    mock_insight_agent: InsightResult,
) -> None:
    headers = {"Authorization": f"Bearer {admin_token}"}
    r = admin_client.post(_URL, json={"pergunta": _PERGUNTA}, headers=headers)
    tipos = [v["tipo"] for v in r.json()["visualizacoes"]]
    assert "grafico" in tipos


def test_grafico_omitted_for_single_row_result(
    admin_client: TestClient,
    admin_token: str,
    monkeypatch: pytest.MonkeyPatch,
    mock_insight_agent: InsightResult,
) -> None:
    single_row = SqlGenerationResult(
        sql="SELECT AVG(avaliacao) AS media FROM avaliacoes_pedidos LIMIT 1000",
        explicacao_seca="Média geral de avaliações.",
        sugestao_grafico="none",
        forcar_tabela=True,
        eh_off_topic=False,
    )

    async def _fake(*args: Any, **kwargs: Any) -> SqlGenerationResult:
        return single_row

    monkeypatch.setattr("app.agents.sql_agent.gerar_sql", _fake)
    headers = {"Authorization": f"Bearer {admin_token}"}
    r = admin_client.post(_URL, json={"pergunta": "Qual a média de avaliação?"}, headers=headers)
    tipos = [v["tipo"] for v in r.json()["visualizacoes"]]
    assert "grafico" not in tipos


def test_tabela_omitted_when_user_asks_only_chart(
    admin_client: TestClient,
    admin_token: str,
    monkeypatch: pytest.MonkeyPatch,
    mock_insight_agent: InsightResult,
) -> None:
    chart_only = SqlGenerationResult(
        sql="SELECT status, COUNT(*) AS total FROM pedidos GROUP BY status LIMIT 1000",
        explicacao_seca="Pedidos agrupados por status.",
        sugestao_grafico="bar",
        grafico_config={"eixo_x": "status", "eixo_y": "total"},
        forcar_tabela=False,
        eh_off_topic=False,
    )

    async def _fake(*args: Any, **kwargs: Any) -> SqlGenerationResult:
        return chart_only

    monkeypatch.setattr("app.agents.sql_agent.gerar_sql", _fake)
    headers = {"Authorization": f"Bearer {admin_token}"}
    r = admin_client.post(
        _URL, json={"pergunta": "Apenas o gráfico de pedidos por status"}, headers=headers
    )
    tipos = [v["tipo"] for v in r.json()["visualizacoes"]]
    assert "tabela" not in tipos


# ---------------------------------------------------------------------------
# Anonimização
# ---------------------------------------------------------------------------


def test_anonimizacao_flag_masks_pii_fields(
    admin_client: TestClient,
    admin_token: str,
    monkeypatch: pytest.MonkeyPatch,
    mock_insight_agent: InsightResult,
) -> None:
    pii_result = SqlGenerationResult(
        sql="SELECT nome_consumidor FROM consumidores LIMIT 1000",
        explicacao_seca="Lista de consumidores.",
        sugestao_grafico="none",
        forcar_tabela=True,
        eh_off_topic=False,
    )

    async def _fake(*args: Any, **kwargs: Any) -> SqlGenerationResult:
        return pii_result

    monkeypatch.setattr("app.agents.sql_agent.gerar_sql", _fake)
    headers = {"Authorization": f"Bearer {admin_token}"}
    r = admin_client.post(
        _URL, json={"pergunta": "Lista consumidores", "anonimizar": True}, headers=headers
    )
    tabelas = [v for v in r.json()["visualizacoes"] if v["tipo"] == "tabela"]
    assert tabelas, "Esperava tabela na resposta"
    for row in tabelas[0]["linhas"]:
        assert not any(str(cell).startswith("Consumidor Teste") for cell in row)


def test_anonimizacao_off_preserves_original_data(
    admin_client: TestClient,
    admin_token: str,
    mock_sql_agent: SqlGenerationResult,
    mock_insight_agent: InsightResult,
) -> None:
    headers = {"Authorization": f"Bearer {admin_token}"}
    r = admin_client.post(_URL, json={"pergunta": _PERGUNTA, "anonimizar": False}, headers=headers)
    assert r.json()["metadados"]["anonimizado"] is False


# ---------------------------------------------------------------------------
# Off-topic / guardrail / errors
# ---------------------------------------------------------------------------


def test_off_topic_question_returns_friendly_error(
    admin_client: TestClient,
    admin_token: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    off_topic = SqlGenerationResult(
        sql="",
        explicacao_seca="",
        sugestao_grafico="none",
        eh_off_topic=True,
        mensagem_off_topic=(
            "Esta ferramenta responde apenas perguntas sobre os dados do e-commerce."
        ),
    )

    async def _fake(*args: Any, **kwargs: Any) -> SqlGenerationResult:
        return off_topic

    monkeypatch.setattr("app.agents.sql_agent.gerar_sql", _fake)
    headers = {"Authorization": f"Bearer {admin_token}"}
    r = admin_client.post(_URL, json={"pergunta": "me escreve um poema"}, headers=headers)
    assert r.status_code == 200
    assert r.json()["erro_amigavel"] is not None


def test_guardrail_rejected_query_returns_400(
    admin_client: TestClient,
    admin_token: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.services.sql_guardrail import QueryNotAllowedError

    async def _fake(*args: Any, **kwargs: Any) -> SqlGenerationResult:
        raise QueryNotAllowedError("Apenas consultas SELECT são permitidas.")

    monkeypatch.setattr("app.agents.sql_agent.gerar_sql", _fake)
    headers = {"Authorization": f"Bearer {admin_token}"}
    r = admin_client.post(_URL, json={"pergunta": "DROP TABLE produtos"}, headers=headers)
    assert r.status_code == 400
    assert r.json()["erro"] == "query_rejeitada"


def test_malformed_request_returns_422(
    admin_client: TestClient,
    admin_token: str,
) -> None:
    headers = {"Authorization": f"Bearer {admin_token}"}
    r = admin_client.post(_URL, json={"pergunta": "ab"}, headers=headers)  # min_length=3
    assert r.status_code == 422


def test_rate_limit_returns_429(
    admin_client: TestClient,
    admin_token: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.errors import GeminiRateLimitError

    async def _fake(*args: Any, **kwargs: Any) -> SqlGenerationResult:
        raise GeminiRateLimitError("rate limit simulado")

    monkeypatch.setattr("app.agents.sql_agent.gerar_sql", _fake)
    headers = {"Authorization": f"Bearer {admin_token}"}
    r = admin_client.post(_URL, json={"pergunta": _PERGUNTA}, headers=headers)
    assert r.status_code == 429


def test_quota_exhausted_returns_503(
    admin_client: TestClient,
    admin_token: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.errors import GeminiQuotaExhaustedError

    async def _fake(*args: Any, **kwargs: Any) -> SqlGenerationResult:
        raise GeminiQuotaExhaustedError("quota esgotada simulada")

    monkeypatch.setattr("app.agents.sql_agent.gerar_sql", _fake)
    headers = {"Authorization": f"Bearer {admin_token}"}
    r = admin_client.post(_URL, json={"pergunta": _PERGUNTA}, headers=headers)
    assert r.status_code == 503


def test_missing_google_api_key_returns_503(
    admin_client: TestClient,
    admin_token: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.errors import GeminiNotConfiguredError

    async def _fake(*args: Any, **kwargs: Any) -> SqlGenerationResult:
        raise GeminiNotConfiguredError()

    monkeypatch.setattr("app.agents.sql_agent.gerar_sql", _fake)
    headers = {"Authorization": f"Bearer {admin_token}"}
    r = admin_client.post(_URL, json={"pergunta": _PERGUNTA}, headers=headers)
    assert r.status_code == 503


# ---------------------------------------------------------------------------
# Retry / fallback
# ---------------------------------------------------------------------------


def test_retry_logic_recovers_from_first_failure(
    admin_client: TestClient,
    admin_token: str,
    monkeypatch: pytest.MonkeyPatch,
    mock_insight_agent: InsightResult,
) -> None:
    calls = {"n": 0}
    success = SqlGenerationResult(
        sql="SELECT nome_produto, total_vendas FROM produtos LIMIT 10",
        explicacao_seca="Top 10 produtos.",
        sugestao_grafico="bar",
        grafico_config={"eixo_x": "nome_produto", "eixo_y": "total_vendas"},
        forcar_tabela=True,
        eh_off_topic=False,
    )

    async def _fake(*args: Any, **kwargs: Any) -> SqlGenerationResult:
        calls["n"] += 1
        if calls["n"] == 1:
            raise ValueError("Erro simulado na primeira tentativa")
        return success

    monkeypatch.setattr("app.agents.sql_agent.gerar_sql", _fake)
    headers = {"Authorization": f"Bearer {admin_token}"}
    r = admin_client.post(_URL, json={"pergunta": _PERGUNTA}, headers=headers)
    assert r.status_code == 200
    assert r.json()["tentativas"] >= 2


def test_fallback_message_after_max_retries(
    admin_client: TestClient,
    admin_token: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def _always_fail(*args: Any, **kwargs: Any) -> SqlGenerationResult:
        raise ValueError("Erro persistente")

    monkeypatch.setattr("app.agents.sql_agent.gerar_sql", _always_fail)
    headers = {"Authorization": f"Bearer {admin_token}"}
    r = admin_client.post(_URL, json={"pergunta": _PERGUNTA}, headers=headers)
    assert r.status_code == 200
    assert r.json()["erro_amigavel"] is not None


def test_limit_forced_on_query_without_limit(
    admin_client: TestClient,
    admin_token: str,
    mock_sql_agent: SqlGenerationResult,
    mock_insight_agent: InsightResult,
) -> None:
    headers = {"Authorization": f"Bearer {admin_token}"}
    r = admin_client.post(_URL, json={"pergunta": _PERGUNTA}, headers=headers)
    sql = r.json().get("sql_gerado", "")
    assert "LIMIT" in sql.upper()


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------


def test_saude_returns_200(admin_client: TestClient) -> None:
    # Arrange / Act
    r = admin_client.get(_HEALTH_URL)
    # Assert
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert "gemini_configurado" in body
    assert "banco_acessivel" in body
