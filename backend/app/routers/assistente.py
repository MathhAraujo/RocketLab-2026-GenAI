"""HTTP layer for the /api/assistente endpoints.

All business logic lives in ``services.assistente_service``. This router
handles HTTP semantics, authentication guards, request validation, and DI only.
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy import Engine

from app.config import settings
from app.dependencies import require_admin
from app.models.usuario import Usuario
from app.schemas.assistente import PerguntaRequest, RespostaAssistente
from app.services.assistente_service import responder_pergunta
from app.services.readonly_db import get_readonly_engine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/assistente", tags=["assistente"])


def get_assistente_engine() -> Engine:
    """Return the cached read-only engine; overridable in tests."""
    return get_readonly_engine()


@router.post(
    "/perguntar",
    response_model=RespostaAssistente,
    summary="Fazer uma pergunta ao assistente de dados",
    responses={
        400: {"description": "Query SQL bloqueada pelo guardrail."},
        401: {"description": "Token ausente ou inválido."},
        403: {"description": "Apenas administradores podem utilizar o assistente."},
        503: {"description": "Serviço de IA não configurado."},
    },
)
async def perguntar(
    req: PerguntaRequest,
    _: Usuario = Depends(require_admin),
    engine: Engine = Depends(get_assistente_engine),
) -> RespostaAssistente:
    """Translate a natural-language question into SQL, execute it, and return results."""
    return await responder_pergunta(
        pergunta=req.pergunta,
        anonimizar=req.anonimizar,
        engine=engine,
    )


@router.get(
    "/saude",
    summary="Health check do assistente",
)
async def saude() -> dict[str, Any]:
    """Report availability of the AI service and the read-only database."""
    gemini_ok = bool(settings.GOOGLE_API_KEY)
    try:
        get_readonly_engine()
        banco_ok = True
    except FileNotFoundError:
        banco_ok = False
    return {"status": "ok", "gemini_configurado": gemini_ok, "banco_acessivel": banco_ok}
