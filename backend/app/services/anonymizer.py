"""Deterministic PII masking for query results.

When the client sets ``anonimizar=true``, rows returned by the agent
are passed through ``anonymize_rows`` before serialization. Masking is
column-based (by column name), deterministic (SHA-1 truncated), and
null-safe.
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Callable
from typing import Any, Final

_HASH_LENGTH: Final[int] = 6
_COMMENT_MAX_LENGTH: Final[int] = 40
_NUMBER_PATTERN: Final[re.Pattern[str]] = re.compile(r"\d{3,}")
_HASH_NAME_COLUMNS: Final[frozenset[str]] = frozenset(
    {"nome_consumidor", "nome_vendedor", "autor_resposta"}
)


def _hash6(value: str) -> str:
    """Return the first 6 hex chars of SHA-1(value)."""
    return hashlib.sha1(value.encode("utf-8")).hexdigest()[:_HASH_LENGTH]


def _mask_cep(value: str | None) -> str | None:
    if not value:
        return value
    return f"{value[:2]}***"


def _redact_comment(value: str | None) -> str | None:
    if not value:
        return value
    trimmed = value[:_COMMENT_MAX_LENGTH]
    if len(value) > _COMMENT_MAX_LENGTH:
        trimmed = f"{trimmed}…"
    return _NUMBER_PATTERN.sub("***", trimmed)


def _hash_name(prefix: str) -> Callable[[str | None], str | None]:
    def _apply(value: str | None) -> str | None:
        if not value:
            return value
        return f"{prefix}_{_hash6(value)}"

    return _apply


PII_TRANSFORMERS: Final[dict[str, Callable[[Any], Any]]] = {
    "nome_consumidor": _hash_name("Consumidor"),
    "nome_vendedor": _hash_name("Vendedor"),
    "autor_resposta": _hash_name("Usuario"),
    "prefixo_cep": _mask_cep,
    "comentario": _redact_comment,
    "titulo_comentario": _redact_comment,
}


def anonymize_rows_with_mapping(
    columns: list[str],
    rows: list[list[Any]],
    enabled: bool,
) -> tuple[list[list[Any]], dict[str, str]]:
    """Apply PII masking and return both the masked rows and a reverse mapping.

    The mapping contains only hash-name columns (nome_consumidor, nome_vendedor,
    autor_resposta) because those produce human-readable tokens that are useful
    to display as a translation legend. CEP and comment masking are irreversible
    and therefore excluded from the mapping.

    Args:
        columns: Ordered list of column names.
        rows: List of rows where each row matches ``columns`` in order.
        enabled: If ``False``, returns ``rows`` unchanged with an empty mapping.

    Returns:
        A tuple of (masked_rows, mapping) where mapping is
        ``{anonymized_token: original_value}``.

    Raises:
        ValueError: If any row length does not match ``columns`` length.
    """
    if not enabled:
        return rows, {}

    transformers = [PII_TRANSFORMERS.get(col) for col in columns]
    is_hash_col = [col in _HASH_NAME_COLUMNS for col in columns]
    mapping: dict[str, str] = {}
    anon_rows: list[list[Any]] = []

    for row in rows:
        new_row: list[Any] = []
        for idx, (transformer, value) in enumerate(zip(transformers, row, strict=True)):
            if transformer is not None:
                masked = transformer(value)
                if is_hash_col[idx] and value is not None and masked is not None:
                    mapping[masked] = str(value)
                new_row.append(masked)
            else:
                new_row.append(value)
        anon_rows.append(new_row)

    return anon_rows, mapping


def anonymize_rows(
    columns: list[str],
    rows: list[list[Any]],
    enabled: bool,
) -> list[list[Any]]:
    """Apply deterministic PII masking to rows based on column names.

    Args:
        columns: Ordered list of column names.
        rows: List of rows where each row matches ``columns`` in order.
        enabled: If ``False``, returns ``rows`` unchanged.

    Returns:
        New list of rows with PII columns masked.

    Raises:
        ValueError: If any row length does not match ``columns`` length.
    """
    if not enabled:
        return rows

    transformers = [PII_TRANSFORMERS.get(col) for col in columns]

    return [
        [
            transformer(value) if transformer else value
            for transformer, value in zip(transformers, row, strict=True)
        ]
        for row in rows
    ]
