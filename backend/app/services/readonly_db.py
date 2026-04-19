"""Read-only SQLAlchemy engine for agent-generated queries."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from sqlalchemy import Engine, create_engine


@lru_cache
def get_readonly_engine(db_path: str = "./database.db") -> Engine:
    """Return a cached read-only engine for the SQLite database.

    The ``mode=ro`` URI flag makes the SQLite driver reject any write
    at the engine level — this is the last line of defense if the
    sqlglot guardrail is bypassed.

    Args:
        db_path: Path to the SQLite database file.

    Returns:
        A SQLAlchemy ``Engine`` configured in read-only mode.

    Raises:
        FileNotFoundError: If ``db_path`` does not exist.
    """
    resolved = Path(db_path).resolve()
    if not resolved.exists():
        raise FileNotFoundError(f"Database file not found: {resolved}")

    uri = f"sqlite:///file:{resolved}?mode=ro&uri=true"
    return create_engine(uri, connect_args={"uri": True})
