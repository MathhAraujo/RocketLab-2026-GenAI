"""SQL query validation against security guardrails.

All agent-generated queries pass through ``validate_and_harden`` before
execution. The function raises ``QueryNotAllowedError`` on any violation
and otherwise returns a hardened SQL string with a safe ``LIMIT``.
"""

from __future__ import annotations

from typing import Final

import sqlglot
from sqlglot import exp

MAX_ROWS: Final[int] = 1000
FORBIDDEN_TABLES: Final[frozenset[str]] = frozenset({"usuarios"})


class QueryNotAllowedError(ValueError):
    """Raised when a SQL query violates security guardrails."""


def validate_and_harden(sql: str) -> str:
    """Validate SQL and return a hardened version with safe ``LIMIT``.

    Checks applied in order:
      1. SQL is parseable as SQLite dialect.
      2. Exactly one statement (no multi-statement injection).
      3. The statement is a ``SELECT`` (no DDL/DML).
      4. No forbidden table is referenced.
      5. ``LIMIT`` is injected or capped to ``MAX_ROWS``.

    Args:
        sql: Raw SQL produced by the agent.

    Returns:
        The SQL with a safe ``LIMIT`` clause.

    Raises:
        QueryNotAllowedError: If any guardrail is violated.
    """
    tree = _parse_single_statement(sql)
    select = _ensure_select(tree)
    _ensure_no_forbidden_tables(select)
    return _enforce_limit(select).sql(dialect="sqlite")


def _parse_single_statement(sql: str) -> exp.Expr:
    try:
        parsed = sqlglot.parse(sql, dialect="sqlite")
    except sqlglot.errors.ParseError as exc:
        raise QueryNotAllowedError(f"SQL malformado: {exc}") from exc

    if len(parsed) != 1 or parsed[0] is None:
        raise QueryNotAllowedError("Apenas uma consulta por vez é permitida.")

    return parsed[0]


def _ensure_select(tree: exp.Expr) -> exp.Select:
    if not isinstance(tree, exp.Select):
        raise QueryNotAllowedError("Apenas consultas SELECT são permitidas.")
    return tree


def _ensure_no_forbidden_tables(tree: exp.Select) -> None:
    for table in tree.find_all(exp.Table):
        if table.name.lower() in FORBIDDEN_TABLES:
            raise QueryNotAllowedError(f"Consultas à tabela '{table.name}' não são permitidas.")


def _enforce_limit(tree: exp.Select) -> exp.Select:
    existing = tree.args.get("limit")
    if existing is None:
        return tree.limit(MAX_ROWS)

    try:
        current = int(existing.expression.name)
    except (ValueError, AttributeError):
        return tree.limit(MAX_ROWS)

    return tree.limit(MAX_ROWS) if current > MAX_ROWS else tree
