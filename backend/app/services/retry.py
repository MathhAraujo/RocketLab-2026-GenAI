"""Async retry loop for LLM agent calls with error-context propagation."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Final, TypeVar

MAX_ATTEMPTS: Final[int] = 3

T = TypeVar("T")


@dataclass
class RetryContext:
    """Error context injected into retried agent calls for self-correction.

    Attributes:
        sql_anterior: The SQL string from the previous failed attempt, if any.
        mensagem_erro: The error message from the previous failure, if any.
    """

    sql_anterior: str | None
    mensagem_erro: str | None


def _extract_sql(exc: BaseException) -> str | None:
    raw = getattr(exc, "sql", None)
    return str(raw) if isinstance(raw, str) else None


async def run_with_retry(
    fn: Callable[[RetryContext | None], Awaitable[T]],
) -> T:
    """Run *fn* up to MAX_ATTEMPTS times, injecting failure context on retries.

    On the first call *fn* receives ``None``. On each subsequent attempt it
    receives a ``RetryContext`` built from the previous exception, allowing the
    agent to self-correct based on the SQL it generated and the error it got.

    Args:
        fn: Async callable that accepts ``RetryContext | None``.

    Returns:
        The first successful return value of *fn*.

    Raises:
        Exception: Re-raises the exception from the last failed attempt after
            all MAX_ATTEMPTS are exhausted.
    """
    context: RetryContext | None = None
    last_exc: Exception | None = None

    for _ in range(MAX_ATTEMPTS):
        try:
            return await fn(context)
        except Exception as exc:
            context = RetryContext(
                sql_anterior=_extract_sql(exc),
                mensagem_erro=str(exc),
            )
            last_exc = exc

    if last_exc is not None:
        raise last_exc
    raise AssertionError("unreachable")  # pragma: no cover
