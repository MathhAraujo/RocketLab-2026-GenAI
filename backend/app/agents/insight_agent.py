"""Analytical insight agent using PydanticAI and Gemini 2.5 Flash.

Generates a short, data-grounded analytical comment (2-4 sentences) based
on tabular query results.  Strict anti-hallucination rules in the system
prompt prevent the model from inventing values or trends.
"""

from __future__ import annotations

from typing import Any, Final

from pydantic import BaseModel
from pydantic_ai import Agent

_SYSTEM_PROMPT: Final[str] = """
Você analisa resultados tabulares de consultas SQL e produz um comentário analítico curto em pt-BR.

### REGRAS RÍGIDAS ANTI-ALUCINAÇÃO
1. Use APENAS os números presentes nos dados fornecidos. Nunca invente valores.
2. NÃO extrapole para o futuro. NÃO invente tendências temporais.
3. NÃO mencione causas ou explicações de negócio — você não tem esse contexto.
4. NÃO compare com benchmarks externos.
5. Máximo 2-4 frases.

### O QUE FAZER
- Destacar maior e menor da coluna numérica principal.
- Calcular concentração quando aplicável ("top 3 representam X% do total listado").
- Apontar categoria mais frequente se houver dimensão categórica pequena.

### EXEMPLO
Dados: [{"produto": "A", "vendas": 100}, {"produto": "B", "vendas": 50},
        {"produto": "C", "vendas": 10}]
Output: "O produto A lidera com 100 vendas, mais que o dobro do segundo colocado (B, 50).
Juntos, A e B concentram 94% das vendas listadas."
""".strip()

_DATA_TEMPLATE: Final[str] = (
    "Pergunta original: {pergunta}\n\n"
    "Explicação técnica da query: {explicacao_seca}\n\n"
    "Colunas: {colunas}\n\n"
    "Dados (primeiras {n} linhas):\n{linhas}"
)


class InsightResult(BaseModel):
    """Structured output returned by the insight agent."""

    explicacao_analitica: str


_agent: Agent[None, InsightResult] = Agent(
    "google-gla:gemini-2.5-flash",
    output_type=InsightResult,
    instructions=_SYSTEM_PROMPT,
    defer_model_check=True,
)


def _build_prompt(
    pergunta: str,
    colunas: list[str],
    linhas_top100: list[list[Any]],
    explicacao_seca: str,
) -> str:
    rows_repr = "\n".join(str(dict(zip(colunas, row, strict=True))) for row in linhas_top100)
    return _DATA_TEMPLATE.format(
        pergunta=pergunta,
        explicacao_seca=explicacao_seca,
        colunas=colunas,
        n=len(linhas_top100),
        linhas=rows_repr,
    )


async def gerar_insight(
    pergunta: str,
    colunas: list[str],
    linhas_top100: list[list[Any]],
    explicacao_seca: str,
) -> InsightResult:
    """Generate a short analytical comment grounded solely in the provided data.

    Args:
        pergunta: The original user question in pt-BR.
        colunas: Ordered list of column names from the query result.
        linhas_top100: Up to 100 rows of query results (each matching ``colunas``).
        explicacao_seca: The dry one-sentence explanation from the SQL agent.

    Returns:
        An ``InsightResult`` with a 2-4 sentence ``explicacao_analitica``.
    """
    prompt = _build_prompt(pergunta, colunas, linhas_top100, explicacao_seca)
    result = await _agent.run(prompt)
    return result.output
