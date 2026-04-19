"""Request and response schemas for the /api/assistente endpoint."""

from __future__ import annotations

from typing import Any, Literal, TypeAlias

from pydantic import BaseModel, ConfigDict, Field

FormatType: TypeAlias = Literal["monetario", "float", "inteiro", "texto"]


class PerguntaRequest(BaseModel):
    """Payload for the /perguntar endpoint."""

    model_config = ConfigDict(extra="forbid")

    pergunta: str = Field(min_length=3, max_length=500)
    anonimizar: bool = False


class TabelaVisualizacao(BaseModel):
    """Tabular visualization block."""

    tipo: Literal["tabela"] = "tabela"
    titulo: str
    colunas: list[str]
    linhas: list[list[Any]]
    formatacao_colunas: dict[str, FormatType] | None = None


class GraficoVisualizacao(BaseModel):
    """Chart visualization block."""

    tipo: Literal["grafico"] = "grafico"
    subtipo: Literal["bar", "line", "pie", "area", "scatter"]
    titulo: str
    eixo_x: str
    eixo_y: str
    dados: list[dict[str, Any]]


Visualizacao: TypeAlias = TabelaVisualizacao | GraficoVisualizacao


class MetadadosResposta(BaseModel):
    """Non-essential metadata about the response generation."""

    anonimizado: bool = False
    linhas_retornadas: int = 0
    usou_insight: bool = False
    motivo: str | None = None


class RespostaAssistente(BaseModel):
    """Full response payload for the /perguntar endpoint."""

    pergunta: str
    sql_gerado: str | None = None
    explicacao: str | None = None
    visualizacoes: list[Visualizacao] = []
    tentativas: int = 1
    erro_amigavel: str | None = None
    metadados: MetadadosResposta
