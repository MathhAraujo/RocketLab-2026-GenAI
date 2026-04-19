"""Centralised exception handlers for domain errors.

All HTTP error mapping lives here so that services and agents never need to
import FastAPI.  Call ``register_exception_handlers(app)`` once during
application startup (in ``main.py``).
"""

from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.services.sql_guardrail import QueryNotAllowedError

logger = logging.getLogger(__name__)

_MSG_GEMINI_NOT_CONFIGURED = "Serviço de IA não configurado. Contate o administrador."
_MSG_AGENT_FAILURE = "Falha interna no agente de análise."
_MSG_RATE_LIMIT = "Muitas requisições em pouco tempo. Aguarde alguns segundos e tente novamente."
_MSG_QUOTA_EXHAUSTED = (
    "Limite diário de requisições da IA atingido. "
    "O serviço será retomado amanhã. Tente novamente mais tarde."
)


class GeminiNotConfiguredError(RuntimeError):
    """Raised when GOOGLE_API_KEY is absent and the AI endpoint is called."""


class AgentFailureError(RuntimeError):
    """Raised when all retry attempts for the AI agent are exhausted."""


class GeminiRateLimitError(RuntimeError):
    """Raised when the Gemini API returns a per-minute rate-limit response (HTTP 429)."""


class GeminiQuotaExhaustedError(RuntimeError):
    """Raised when the Gemini API daily quota is exhausted."""


def register_exception_handlers(app: FastAPI) -> None:
    """Register domain exception → HTTP response mappings on *app*.

    Args:
        app: The FastAPI application instance.
    """

    @app.exception_handler(QueryNotAllowedError)
    async def handle_query_not_allowed(request: Request, exc: QueryNotAllowedError) -> JSONResponse:
        logger.warning("Consulta rejeitada pelo guardrail: %s", exc)
        return JSONResponse(
            status_code=400,
            content={"erro": "query_rejeitada", "motivo": str(exc)},
        )

    @app.exception_handler(GeminiNotConfiguredError)
    async def handle_gemini_not_configured(
        request: Request, exc: GeminiNotConfiguredError
    ) -> JSONResponse:
        logger.error("Tentativa de uso do agente sem GOOGLE_API_KEY configurada")
        return JSONResponse(
            status_code=503,
            content={"detail": _MSG_GEMINI_NOT_CONFIGURED},
        )

    @app.exception_handler(AgentFailureError)
    async def handle_agent_failure(request: Request, exc: AgentFailureError) -> JSONResponse:
        logger.exception("Falha irrecuperável no agente após retentativas: %s", exc)
        return JSONResponse(
            status_code=500,
            content={"detail": _MSG_AGENT_FAILURE},
        )

    @app.exception_handler(GeminiRateLimitError)
    async def handle_rate_limit(request: Request, exc: GeminiRateLimitError) -> JSONResponse:
        logger.warning("Gemini rate limit atingido: %s", exc)
        return JSONResponse(status_code=429, content={"detail": _MSG_RATE_LIMIT})

    @app.exception_handler(GeminiQuotaExhaustedError)
    async def handle_quota_exhausted(
        request: Request, exc: GeminiQuotaExhaustedError
    ) -> JSONResponse:
        logger.error("Gemini quota diária esgotada: %s", exc)
        return JSONResponse(status_code=503, content={"detail": _MSG_QUOTA_EXHAUSTED})
