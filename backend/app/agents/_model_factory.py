"""Shared builder for the Gemini model reference used by PydanticAI agents."""

from __future__ import annotations

from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider

from app.config import settings

_MODEL_NAME = "gemini-2.5-flash"
_FALLBACK_MODEL_REF = f"google-gla:{_MODEL_NAME}"


def build_gemini_model() -> GoogleModel | str:
    """Return a configured GoogleModel, or a string ref when the API key is absent.

    The string form lets agents be instantiated at module load time without
    failing — real API calls still fail later via GeminiNotConfiguredError.
    """
    if settings.GOOGLE_API_KEY:
        return GoogleModel(_MODEL_NAME, provider=GoogleProvider(api_key=settings.GOOGLE_API_KEY))
    return _FALLBACK_MODEL_REF
