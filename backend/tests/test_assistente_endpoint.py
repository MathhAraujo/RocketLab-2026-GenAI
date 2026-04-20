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


def test_anonimizacao_flag_sets_anonimizado_metadata(
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
    body = r.json()
    assert body["metadados"]["anonimizado"] is True
    assert "traducao_anonimizacao" in body


def test_anonimizacao_mapping_returned_when_pii_present(
    admin_client: TestClient,
    admin_token: str,
    monkeypatch: pytest.MonkeyPatch,
    mock_insight_agent: InsightResult,
) -> None:
    """Visualizações mostram dados reais; mapeamento expõe a tradução token→real."""
    pii_result = SqlGenerationResult(
        sql="SELECT nome_consumidor FROM consumidores LIMIT 1000",
        explicacao_seca="Lista de consumidores.",
        sugestao_grafico="none",
        forcar_tabela=True,
        eh_off_topic=False,
    )
    real_names = ["Milena Borges", "Lucas Faria"]

    async def _fake_sql(*args: Any, **kwargs: Any) -> SqlGenerationResult:
        return pii_result

    async def _fake_query(sql: str, engine: Any) -> tuple[list[str], list[list[Any]]]:
        return ["nome_consumidor"], [[name] for name in real_names]

    monkeypatch.setattr("app.agents.sql_agent.gerar_sql", _fake_sql)
    monkeypatch.setattr("app.services.assistente_service._executar_consulta", _fake_query)
    headers = {"Authorization": f"Bearer {admin_token}"}
    r = admin_client.post(
        _URL, json={"pergunta": "lista consumidores", "anonimizar": True}, headers=headers
    )
    body = r.json()
    assert r.status_code == 200
    # Tabela exibe dados reais (não anonimizados)
    tabelas = [v for v in body["visualizacoes"] if v["tipo"] == "tabela"]
    assert tabelas, "Esperava tabela na resposta"
    cell_values = [row[0] for row in tabelas[0]["linhas"]]
    assert set(cell_values) == set(real_names)
    # Mapeamento de tradução presente e correto
    mapping = body["traducao_anonimizacao"]
    assert mapping is not None
    assert set(mapping.values()) == set(real_names)


def test_anonimizacao_off_preserves_original_data(
    admin_client: TestClient,
    admin_token: str,
    mock_sql_agent: SqlGenerationResult,
    mock_insight_agent: InsightResult,
) -> None:
    headers = {"Authorization": f"Bearer {admin_token}"}
    r = admin_client.post(_URL, json={"pergunta": _PERGUNTA, "anonimizar": False}, headers=headers)
    body = r.json()
    assert body["metadados"]["anonimizado"] is False
    assert body["traducao_anonimizacao"] is None


def test_anonimizacao_default_is_true(
    admin_client: TestClient,
    admin_token: str,
    mock_sql_agent: SqlGenerationResult,
    mock_insight_agent: InsightResult,
) -> None:
    """Omitir anonimizar no payload deve usar True como padrão."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    r = admin_client.post(_URL, json={"pergunta": _PERGUNTA}, headers=headers)
    assert r.json()["metadados"]["anonimizado"] is True


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


def test_gemini_unavailable_returns_503_with_specific_message(
    admin_client: TestClient,
    admin_token: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.errors import GeminiUnavailableError

    async def _fake(*args: Any, **kwargs: Any) -> SqlGenerationResult:
        raise GeminiUnavailableError("503 UNAVAILABLE simulado")

    monkeypatch.setattr("app.agents.sql_agent.gerar_sql", _fake)
    headers = {"Authorization": f"Bearer {admin_token}"}
    r = admin_client.post(_URL, json={"pergunta": _PERGUNTA}, headers=headers)
    assert r.status_code == 503
    assert "sobrecarregado" in r.json()["detail"].lower()


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
# Chart axis validation (regression for empty-chart bug)
# ---------------------------------------------------------------------------


def test_hallucinated_eixo_y_falls_back_to_first_numeric_column(
    admin_client: TestClient,
    admin_token: str,
    monkeypatch: pytest.MonkeyPatch,
    mock_insight_agent: InsightResult,
) -> None:
    """eixo_y that doesn't match any column is replaced by first numeric column."""
    # Arrange — "contagem" does not exist in ['nome_produto', 'total_vendas']
    wrong_y = SqlGenerationResult(
        sql="SELECT nome_produto, total_vendas FROM produtos ORDER BY total_vendas DESC LIMIT 10",
        explicacao_seca="Produtos com mais vendas.",
        sugestao_grafico="bar",
        grafico_config={"eixo_x": "nome_produto", "eixo_y": "contagem"},
        forcar_tabela=True,
        eh_off_topic=False,
    )

    async def _fake(*args: Any, **kwargs: Any) -> SqlGenerationResult:
        return wrong_y

    monkeypatch.setattr("app.agents.sql_agent.gerar_sql", _fake)
    headers = {"Authorization": f"Bearer {admin_token}"}
    # Act
    r = admin_client.post(_URL, json={"pergunta": "produtos mais vendidos"}, headers=headers)
    # Assert
    graficos = [v for v in r.json()["visualizacoes"] if v["tipo"] == "grafico"]
    assert len(graficos) == 1, "Esperava exatamente um gráfico na resposta"
    assert graficos[0]["eixo_y"] == "total_vendas", (
        f"eixo_y deveria ser 'total_vendas', mas foi '{graficos[0]['eixo_y']}'"
    )


def test_grafico_config_none_picks_first_numeric_column_not_second_column(
    admin_client: TestClient,
    admin_token: str,
    monkeypatch: pytest.MonkeyPatch,
    mock_insight_agent: InsightResult,
) -> None:
    """When grafico_config is None and columns[1] is a string, eixo_y must be first numeric col."""
    # Arrange — columns will be ['nome_produto', 'categoria_produto', 'total_vendas'];
    # old fallback: columns[1] = 'categoria_produto' (string) → empty chart
    no_config = SqlGenerationResult(
        sql=(
            "SELECT nome_produto, categoria_produto, total_vendas "
            "FROM produtos ORDER BY total_vendas DESC LIMIT 10"
        ),
        explicacao_seca="Produtos com categorias.",
        sugestao_grafico="bar",
        grafico_config=None,
        forcar_tabela=True,
        eh_off_topic=False,
    )

    async def _fake(*args: Any, **kwargs: Any) -> SqlGenerationResult:
        return no_config

    monkeypatch.setattr("app.agents.sql_agent.gerar_sql", _fake)
    headers = {"Authorization": f"Bearer {admin_token}"}
    # Act
    r = admin_client.post(_URL, json={"pergunta": "categoria por produto"}, headers=headers)
    # Assert
    graficos = [v for v in r.json()["visualizacoes"] if v["tipo"] == "grafico"]
    assert len(graficos) == 1
    assert graficos[0]["eixo_y"] == "total_vendas", (
        f"eixo_y deveria ser 'total_vendas', mas foi '{graficos[0]['eixo_y']}'"
    )


def test_no_numeric_column_produces_no_chart_and_fallback_table(
    admin_client: TestClient,
    admin_token: str,
    monkeypatch: pytest.MonkeyPatch,
    mock_insight_agent: InsightResult,
) -> None:
    """When all columns are strings and forcar_tabela=False, fallback table is added."""
    # Arrange — no numeric column; forcar_tabela=False → old code renders empty chart with no table
    all_strings = SqlGenerationResult(
        sql="SELECT nome_produto, categoria_produto FROM produtos LIMIT 10",
        explicacao_seca="Produtos e categorias.",
        sugestao_grafico="bar",
        grafico_config=None,
        forcar_tabela=False,
        eh_off_topic=False,
    )

    async def _fake(*args: Any, **kwargs: Any) -> SqlGenerationResult:
        return all_strings

    monkeypatch.setattr("app.agents.sql_agent.gerar_sql", _fake)
    headers = {"Authorization": f"Bearer {admin_token}"}
    # Act
    r = admin_client.post(_URL, json={"pergunta": "nomes e categorias"}, headers=headers)
    vizs = r.json()["visualizacoes"]
    # Assert
    assert not any(v["tipo"] == "grafico" for v in vizs), "Não deve ter gráfico sem coluna numérica"
    assert any(v["tipo"] == "tabela" for v in vizs), "Deve ter tabela de fallback"


def test_hallucinated_eixo_x_falls_back_to_first_column(
    admin_client: TestClient,
    admin_token: str,
    monkeypatch: pytest.MonkeyPatch,
    mock_insight_agent: InsightResult,
) -> None:
    """eixo_x that doesn't match any column is replaced by columns[0]."""
    wrong_x = SqlGenerationResult(
        sql="SELECT nome_produto, total_vendas FROM produtos ORDER BY total_vendas DESC LIMIT 10",
        explicacao_seca="Produtos.",
        sugestao_grafico="bar",
        grafico_config={"eixo_x": "produto", "eixo_y": "total_vendas"},
        forcar_tabela=True,
        eh_off_topic=False,
    )

    async def _fake(*args: Any, **kwargs: Any) -> SqlGenerationResult:
        return wrong_x

    monkeypatch.setattr("app.agents.sql_agent.gerar_sql", _fake)
    headers = {"Authorization": f"Bearer {admin_token}"}
    r = admin_client.post(_URL, json={"pergunta": "produtos mais vendidos"}, headers=headers)
    graficos = [v for v in r.json()["visualizacoes"] if v["tipo"] == "grafico"]
    assert len(graficos) == 1
    assert graficos[0]["eixo_x"] == "nome_produto", (
        f"eixo_x deveria ser 'nome_produto', mas foi '{graficos[0]['eixo_x']}'"
    )


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
