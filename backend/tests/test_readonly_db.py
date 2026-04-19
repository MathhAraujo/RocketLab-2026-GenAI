"""Tests for readonly_db.get_readonly_engine.

All tests follow the AAA pattern. Import will fail until TASK-07 creates
the module — that is the intended red state.

Uses the ``tmp_path`` pytest fixture to create a minimal on-disk SQLite
database so the engine can open a real file (required by mode=ro URI).
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from app.services.readonly_db import get_readonly_engine

_CREATE_TABLE: str = "CREATE TABLE produtos (id INTEGER PRIMARY KEY, nome TEXT)"
_SEED_ROW: str = "INSERT INTO produtos VALUES (1, 'Camiseta')"


def _seed_db(path: Path) -> None:
    conn = sqlite3.connect(str(path))
    conn.execute(_CREATE_TABLE)
    conn.execute(_SEED_ROW)
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------


def test_readonly_engine_executes_select(tmp_path: Path) -> None:
    db_file = tmp_path / "test.db"
    _seed_db(db_file)
    engine = get_readonly_engine(str(db_file))

    with engine.connect() as conn:
        rows = conn.execute(text("SELECT id, nome FROM produtos")).fetchall()

    assert rows == [(1, "Camiseta")]


# ---------------------------------------------------------------------------
# Write rejection
# ---------------------------------------------------------------------------


def test_readonly_engine_rejects_insert(tmp_path: Path) -> None:
    db_file = tmp_path / "test.db"
    _seed_db(db_file)
    engine = get_readonly_engine(str(db_file))

    with pytest.raises(OperationalError):
        with engine.connect() as conn:
            conn.execute(text("INSERT INTO produtos VALUES (2, 'Calça')"))


def test_readonly_engine_rejects_update(tmp_path: Path) -> None:
    db_file = tmp_path / "test.db"
    _seed_db(db_file)
    engine = get_readonly_engine(str(db_file))

    with pytest.raises(OperationalError):
        with engine.connect() as conn:
            conn.execute(text("UPDATE produtos SET nome = 'Bermuda' WHERE id = 1"))


def test_readonly_engine_rejects_delete(tmp_path: Path) -> None:
    db_file = tmp_path / "test.db"
    _seed_db(db_file)
    engine = get_readonly_engine(str(db_file))

    with pytest.raises(OperationalError):
        with engine.connect() as conn:
            conn.execute(text("DELETE FROM produtos WHERE id = 1"))


# ---------------------------------------------------------------------------
# Missing file
# ---------------------------------------------------------------------------


def test_missing_database_file_raises(tmp_path: Path) -> None:
    nonexistent = str(tmp_path / "does_not_exist.db")

    with pytest.raises(FileNotFoundError):
        get_readonly_engine(nonexistent)
