"""SQL generation agent using PydanticAI and Gemini 2.5 Flash.

Translates natural-language questions into validated SELECT queries and
returns visualisation hints.  The agent instance is created once at
module level; real API calls happen only inside ``gerar_sql``.
"""

from __future__ import annotations

from typing import Final

from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider

from app.agents.schema_context import SCHEMA_BLOCK
from app.config import settings
from app.errors import GeminiNotConfiguredError
from app.services.retry import RetryContext

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
- Top N categórico (N <= 20) com uma medida -> bar
- Série temporal com uma medida -> line
- Proporção de um todo (N <= 6) -> pie
- Série temporal com 2+ medidas -> area
- Correlação entre 2 medidas -> scatter
- 1 linha / 1 valor -> sem gráfico (`sugestao_grafico="none"`)
- Usuário pede tipo específico -> respeitar
- Usuário diz "apenas gráfico" / "sem tabela" -> `forcar_tabela=false`

### IDIOMA
Português do Brasil. `explicacao_seca` com no máximo 2 frases.

### EXEMPLOS

Pergunta: "Top 10 produtos mais vendidos"
-> sql: SELECT nome_produto, total_vendas FROM produtos ORDER BY total_vendas DESC LIMIT 10
-> sugestao_grafico: "bar"
-> grafico_config: {{"eixo_x": "nome_produto", "eixo_y": "total_vendas"}}
-> forcar_tabela: true
-> explicacao_seca: "Listei os 10 produtos com maior volume de vendas, ordenados decrescente."
-> eh_off_topic: false

Pergunta: "Receita total por categoria"
-> sql: SELECT p.categoria_produto, SUM(ip.preco_BRL + ip.preco_frete) AS receita_total FROM itens_pedidos ip JOIN produtos p ON ip.id_produto = p.id_produto GROUP BY p.categoria_produto ORDER BY receita_total DESC LIMIT 20
-> sugestao_grafico: "bar"
-> grafico_config: {{"eixo_x": "categoria_produto", "eixo_y": "receita_total"}}
-> forcar_tabela: true

Pergunta: "Pedidos por estado"
-> sql: SELECT c.estado, COUNT(p.id_pedido) AS total_pedidos FROM pedidos p JOIN consumidores c ON p.id_consumidor = c.id_consumidor GROUP BY c.estado ORDER BY total_pedidos DESC LIMIT 50
-> sugestao_grafico: "bar"
-> grafico_config: {{"eixo_x": "estado", "eixo_y": "total_pedidos"}}
-> forcar_tabela: true

Pergunta: "Receita total por mês"
-> sql: SELECT strftime('%Y-%m', p.pedido_compra_timestamp) AS mes, SUM(ip.preco_BRL + ip.preco_frete) AS receita_total FROM pedidos p JOIN itens_pedidos ip ON p.id_pedido = ip.id_pedido WHERE p.pedido_compra_timestamp IS NOT NULL GROUP BY mes ORDER BY mes LIMIT 1000
-> sugestao_grafico: "line"
-> grafico_config: {{"eixo_x": "mes", "eixo_y": "receita_total"}}
-> forcar_tabela: true

Pergunta: "me escreve um poema sobre pedidos"
-> sql: ""
-> eh_off_topic: true
-> mensagem_off_topic: "Esta ferramenta é específica para análise de dados do e-commerce."
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


class SqlGenerationResult(BaseModel):
    """Structured output returned by the SQL generation agent."""

    sql: str = ""
    explicacao_seca: str = ""
    sugestao_grafico: str = Field(default="none")
    grafico_config: GraficoConfig | None = None
    forcar_tabela: bool = True
    eh_off_topic: bool = False
    mensagem_off_topic: str | None = None


def _make_agent() -> Agent[None, SqlGenerationResult]:
    model: GoogleModel | str = (
        GoogleModel("gemini-2.5-flash", provider=GoogleProvider(api_key=settings.GOOGLE_API_KEY))
        if settings.GOOGLE_API_KEY
        else "google-gla:gemini-2.5-flash"
    )
    return Agent(
        model, output_type=SqlGenerationResult, instructions=_SYSTEM_PROMPT, defer_model_check=True
    )


_agent = _make_agent()


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
    result = await _agent.run(prompt)
    return result.output
