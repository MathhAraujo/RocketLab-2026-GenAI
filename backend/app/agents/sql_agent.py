"""SQL generation agent using PydanticAI and Gemini 2.5 Flash.

Translates natural-language questions into validated SELECT queries and
returns visualisation hints.  The agent instance is created once at
module level; real API calls happen only inside ``gerar_sql``.
"""

from __future__ import annotations

from typing import Final, NoReturn

from google.genai.errors import APIError as GoogleAPIError
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.exceptions import ModelHTTPError

from app.agents._model_factory import build_gemini_model
from app.agents.schema_context import SCHEMA_BLOCK
from app.config import settings
from app.errors import (
    GeminiNotConfiguredError,
    GeminiQuotaExhaustedError,
    GeminiRateLimitError,
    GeminiUnavailableError,
)
from app.schemas.assistente import FormatType
from app.services.retry import RetryContext

_HTTP_RATE_LIMIT: Final[int] = 429
_HTTP_SERVICE_UNAVAILABLE: Final[int] = 503

_SYSTEM_PROMPT: Final[str] = f"""
Você é um assistente analítico especializado em consultas de dados de um e-commerce.
Seu papel é converter perguntas em linguagem natural (pt-BR) em queries SQL para SQLite
e sugerir visualizações adequadas.

### REGRAS DE SEGURANÇA (INVIOLÁVEIS)
1. Gere APENAS consultas SELECT. NUNCA gere INSERT, UPDATE, DELETE, DROP, ALTER,
   CREATE, TRUNCATE, REPLACE ou qualquer DDL/DML.
2. NUNCA consulte a tabela `usuarios`. Ela contém senhas e está fora do seu escopo.
3. SEMPRE inclua LIMIT em suas queries (padrão: LIMIT 1000 quando o usuário não especifica).
4. Use APENAS as tabelas e colunas descritas no schema abaixo. Nunca invente nomes.
5. Se a pergunta não for sobre análise de dados do e-commerce, defina `eh_off_topic=true`
   e explique educadamente em `mensagem_off_topic`.

### SCHEMA DO BANCO
{SCHEMA_BLOCK}

### REGRAS DE MODELAGEM
- Receita total de um pedido = SUM(preco_BRL + preco_frete) em itens_pedidos agrupado por id_pedido.
- Receita por categoria: join itens_pedidos -> produtos, GROUP BY categoria_produto.
- Receita por estado: join itens_pedidos -> pedidos -> consumidores, GROUP BY estado.
- `pedidos.entrega_no_prazo` é String — use = 'Sim' ou = 'Não' (maiúscula, acento). NUNCA minúsculas nem TRUE/FALSE.
- Prefira joins a partir das tabelas de fato em vez de colunas desnormalizadas em `produtos`,
  exceto quando a pergunta for sobre elas.

### ESCOLHA DE VISUALIZAÇÃO
Escolha o tipo de gráfico (`sugestao_grafico`) que melhor representa os dados retornados.
Valores válidos: "bar", "line", "pie", "area", "scatter", "none".
Se o usuário solicitar um tipo específico, respeite-o.
Se o usuário disser "apenas gráfico" ou "sem tabela", defina `forcar_tabela=false`.

Em `grafico_config.eixo_x` e `grafico_config.eixo_y`, use EXATAMENTE os nomes das colunas
do SELECT — incluindo aliases definidos com AS. Nunca invente nomes que não aparecem no SELECT.
Exemplo: se o SELECT tem `COUNT(*) AS total_pedidos`, use `"total_pedidos"` em `eixo_y`.

### FORMATAÇÃO DE COLUNAS
Para toda coluna no resultado, preencha `formatacao_colunas` como uma LISTA de objetos
`{{"coluna": "<nome>", "tipo": "<tipo>"}}`. Tipos disponíveis:
- "monetario": valores financeiros em BRL (preços, fretes, receitas, totais monetários)
- "float": decimais sem contexto monetário (avaliações, médias, pesos, ratios)
- "inteiro": contagens, quantidades, IDs numéricos
- "texto": strings, datas, categorias — não formatar como número
Use o contexto semântico da pergunta e do alias AS, não apenas o nome da coluna.
Exemplo: `[{{"coluna": "receita_total", "tipo": "monetario"}}, {{"coluna": "media", "tipo": "float"}}]`.

### IDIOMA
Português do Brasil. `explicacao_seca` com no máximo 2 frases.
""".strip()

_RETRY_SUFFIX: Final[str] = (
    "\n\nSua tentativa anterior falhou com o seguinte erro:\n"
    "SQL gerado: {sql_anterior}\n"
    "Erro: {mensagem_erro}\n\n"
    "Corrija o problema e gere uma nova query. "
    "Lembre-se das regras de segurança: apenas SELECT, nunca `usuarios`, sempre LIMIT."
)


class GraficoConfig(BaseModel):
    """Axis configuration for a chart visualisation.

    Using a typed model (instead of ``dict``) avoids the ``additionalProperties``
    restriction that causes Gemini to drop the entire field.
    """

    eixo_x: str = ""
    eixo_y: str = ""


class FormatacaoColuna(BaseModel):
    """Single column-format entry.

    A flat list of these replaces ``dict[str, FormatType]`` so that the JSON
    schema uses ``items`` instead of ``additionalProperties``, which Gemini
    does not support.
    """

    coluna: str
    tipo: FormatType


class SqlGenerationResult(BaseModel):
    """Structured output returned by the SQL generation agent."""

    sql: str = ""
    explicacao_seca: str = ""
    sugestao_grafico: str = Field(default="none")
    grafico_config: GraficoConfig | None = None
    forcar_tabela: bool = True
    eh_off_topic: bool = False
    mensagem_off_topic: str | None = None
    formatacao_colunas: list[FormatacaoColuna] | None = None


def _make_agent() -> Agent[None, SqlGenerationResult]:
    return Agent(
        build_gemini_model(),
        output_type=SqlGenerationResult,
        instructions=_SYSTEM_PROMPT,
        defer_model_check=True,
    )


_agent = _make_agent()


def _classify_http_error(exc: ModelHTTPError) -> NoReturn:
    """Convert a ModelHTTPError into the appropriate domain exception."""
    if exc.status_code == _HTTP_RATE_LIMIT:
        body_str = str(exc.body or "").lower()
        if "quota" in body_str:
            raise GeminiQuotaExhaustedError(str(exc)) from exc
        raise GeminiRateLimitError(str(exc)) from exc
    if exc.status_code == _HTTP_SERVICE_UNAVAILABLE:
        raise GeminiUnavailableError(str(exc)) from exc
    raise exc


def _classify_google_error(exc: GoogleAPIError) -> NoReturn:
    """Convert a google-genai APIError into the appropriate domain exception.

    The Google SDK raises APIError (not ModelHTTPError) for HTTP 4xx/5xx responses.
    """
    if exc.code == _HTTP_RATE_LIMIT:
        body_str = str(exc.details or "").lower()
        if "quota" in body_str:
            raise GeminiQuotaExhaustedError(str(exc)) from exc
        raise GeminiRateLimitError(str(exc)) from exc
    if exc.code == _HTTP_SERVICE_UNAVAILABLE:
        raise GeminiUnavailableError(str(exc)) from exc
    raise exc


def _build_prompt(pergunta: str, retry_context: RetryContext | None) -> str:
    if retry_context is None:
        return pergunta
    return pergunta + _RETRY_SUFFIX.format(
        sql_anterior=retry_context.sql_anterior or "",
        mensagem_erro=retry_context.mensagem_erro or "",
    )


async def gerar_sql(
    pergunta: str,
    retry_context: RetryContext | None = None,
) -> SqlGenerationResult:
    """Generate a SQL query and visualisation hints from a natural-language question.

    Args:
        pergunta: The user's question in natural language (pt-BR).
        retry_context: Optional context from a previous failed attempt, used
            so the agent can self-correct.

    Returns:
        A ``SqlGenerationResult`` with the SQL, explanation and chart hints.

    Raises:
        GeminiNotConfiguredError: If ``GOOGLE_API_KEY`` is not set.
    """
    if not settings.GOOGLE_API_KEY:
        raise GeminiNotConfiguredError("GOOGLE_API_KEY não configurada.")
    prompt = _build_prompt(pergunta, retry_context)
    try:
        result = await _agent.run(prompt)
        return result.output
    except ModelHTTPError as exc:
        _classify_http_error(exc)
    except GoogleAPIError as exc:
        _classify_google_error(exc)
