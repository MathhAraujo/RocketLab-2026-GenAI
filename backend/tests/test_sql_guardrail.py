"""Tests for sql_guardrail.validate_and_harden.

All tests follow the AAA pattern. This module imports from
app.services.sql_guardrail, which does not exist until TASK-03,
so pytest will fail at collection — that is the intended red state.
"""

from __future__ import annotations

import pytest

from app.services.sql_guardrail import QueryNotAllowedError, validate_and_harden

_VALID_SELECT = "SELECT id_produto, nome_produto FROM produtos LIMIT 10"


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------


def test_allow_valid_select() -> None:
    result = validate_and_harden(_VALID_SELECT)

    assert "SELECT" in result.upper()
    assert "LIMIT" in result.upper()


# ---------------------------------------------------------------------------
# DDL / DML blocking
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "sql",
    [
        "INSERT INTO produtos (nome_produto) VALUES ('x')",
        "UPDATE produtos SET nome_produto = 'x' WHERE id_produto = '1'",
        "DELETE FROM produtos WHERE id_produto = '1'",
        "DROP TABLE produtos",
        "ALTER TABLE produtos ADD COLUMN foo TEXT",
        "CREATE TABLE foo (id INTEGER PRIMARY KEY)",
        "TRUNCATE TABLE produtos",
    ],
    ids=["insert", "update", "delete", "drop", "alter", "create_table", "truncate"],
)
def test_block_ddl_and_dml(sql: str) -> None:
    with pytest.raises(QueryNotAllowedError):
        validate_and_harden(sql)


def test_block_multiple_statements() -> None:
    sql = "SELECT 1; DROP TABLE produtos;"

    with pytest.raises(QueryNotAllowedError):
        validate_and_harden(sql)


def test_block_uppercase_and_lowercase_ddl() -> None:
    lowercase = "insert into produtos (nome_produto) values ('x')"
    mixed_case = "Insert Into produtos (nome_produto) values ('x')"

    with pytest.raises(QueryNotAllowedError):
        validate_and_harden(lowercase)
    with pytest.raises(QueryNotAllowedError):
        validate_and_harden(mixed_case)


# ---------------------------------------------------------------------------
# Forbidden table: usuarios
# ---------------------------------------------------------------------------


def test_block_usuarios_in_from() -> None:
    sql = "SELECT id_usuario FROM usuarios"

    with pytest.raises(QueryNotAllowedError):
        validate_and_harden(sql)


def test_block_usuarios_in_join() -> None:
    sql = "SELECT p.id_pedido FROM pedidos p JOIN usuarios u ON u.id_usuario = p.id_consumidor"

    with pytest.raises(QueryNotAllowedError):
        validate_and_harden(sql)


def test_block_usuarios_in_subquery() -> None:
    sql = "SELECT * FROM pedidos WHERE id_consumidor IN (SELECT id_usuario FROM usuarios)"

    with pytest.raises(QueryNotAllowedError):
        validate_and_harden(sql)


def test_block_usuarios_case_insensitive() -> None:
    for table_name in ("USUARIOS", "Usuarios", "uSuArIoS"):
        sql = f"SELECT id_usuario FROM {table_name}"
        with pytest.raises(QueryNotAllowedError):
            validate_and_harden(sql)


# ---------------------------------------------------------------------------
# LIMIT injection and capping
# ---------------------------------------------------------------------------


def test_inject_limit_when_missing() -> None:
    sql = "SELECT nome_produto FROM produtos"

    result = validate_and_harden(sql)

    assert "1000" in result


def test_respect_existing_limit_within_max() -> None:
    sql = "SELECT nome_produto FROM produtos LIMIT 50"

    result = validate_and_harden(sql)

    assert "50" in result
    assert "1000" not in result


def test_cap_limit_above_max() -> None:
    sql = "SELECT nome_produto FROM produtos LIMIT 5000"

    result = validate_and_harden(sql)

    assert "1000" in result
    assert "5000" not in result


def test_cap_limit_when_value_is_non_integer_expression() -> None:
    # LIMIT NULL parses but int() raises ValueError — branch must cap to MAX_ROWS
    sql = "SELECT nome_produto FROM produtos LIMIT NULL"

    result = validate_and_harden(sql)

    assert "1000" in result


# ---------------------------------------------------------------------------
# Error cases
# ---------------------------------------------------------------------------


def test_malformed_sql_raises() -> None:
    sql = "SELET !! FRMO"

    with pytest.raises(QueryNotAllowedError):
        validate_and_harden(sql)


def test_empty_sql_raises() -> None:
    with pytest.raises(QueryNotAllowedError):
        validate_and_harden("")


def test_non_select_expression_raises() -> None:
    for sql in (
        "EXPLAIN SELECT * FROM produtos",
        "PRAGMA table_info(produtos)",
    ):
        with pytest.raises(QueryNotAllowedError):
            validate_and_harden(sql)
