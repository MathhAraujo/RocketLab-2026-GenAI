"""Tests for retry.run_with_retry.

All tests follow the AAA pattern. Imports will fail until TASK-08 creates
the module — that is the intended red state.
"""

from __future__ import annotations

import pytest

from app.services.retry import MAX_ATTEMPTS, RetryContext, run_with_retry

pytestmark = pytest.mark.asyncio


# ---------------------------------------------------------------------------
# Successful attempts
# ---------------------------------------------------------------------------


async def test_succeeds_on_first_attempt() -> None:
    call_count = 0

    async def fn(ctx: RetryContext | None) -> str:
        nonlocal call_count
        call_count += 1
        return "ok"

    result = await run_with_retry(fn)

    assert result == "ok"
    assert call_count == 1


async def test_succeeds_on_second_attempt() -> None:
    call_count = 0

    async def fn(ctx: RetryContext | None) -> str:
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise ValueError("primeira falha")
        return "recuperado"

    result = await run_with_retry(fn)

    assert result == "recuperado"
    assert call_count == 2


async def test_succeeds_on_third_attempt() -> None:
    call_count = 0

    async def fn(ctx: RetryContext | None) -> str:
        nonlocal call_count
        call_count += 1
        if call_count < MAX_ATTEMPTS:
            raise ValueError(f"falha {call_count}")
        return "recuperado"

    result = await run_with_retry(fn)

    assert result == "recuperado"
    assert call_count == MAX_ATTEMPTS


# ---------------------------------------------------------------------------
# Exhausted retries
# ---------------------------------------------------------------------------


async def test_fails_after_max_retries() -> None:
    async def fn(ctx: RetryContext | None) -> str:
        raise RuntimeError("falha permanente")

    with pytest.raises(RuntimeError, match="falha permanente"):
        await run_with_retry(fn)


# ---------------------------------------------------------------------------
# Context propagation
# ---------------------------------------------------------------------------


async def test_passes_error_context_to_next_attempt() -> None:
    received: list[RetryContext | None] = []

    async def fn(ctx: RetryContext | None) -> str:
        received.append(ctx)
        if ctx is None:
            raise ValueError("falha inicial")
        return "recuperado"

    await run_with_retry(fn)

    assert received[0] is None
    assert received[1] is not None
    assert received[1].mensagem_erro == "falha inicial"
