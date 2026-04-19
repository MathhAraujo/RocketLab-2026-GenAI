"""Read-only SQLAlchemy engine for agent-generated queries."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from sqlalchemy import Engine, create_engine

_SQLITE_PREFIX = "sqlite:///"


def _path_from_database_url(url: str) -> str:
    """Extract the file-system path from a ``sqlite:///`` URL.

    Args:
        url: A SQLAlchemy SQLite URL such as ``sqlite:////data/db.db``
            or ``sqlite:///./database.db``.

    Returns:
        The raw path string after the ``sqlite:///`` prefix.

    Raises:
        ValueError: If *url* does not start with ``sqlite:///``.
    """
    if not url.startswith(_SQLITE_PREFIX):
        raise ValueError(f"Only SQLite DATABASE_URLs are supported: {url!r}")
    return url[len(_SQLITE_PREFIX) :]


@lru_cache
def get_readonly_engine(db_path: str | None = None) -> Engine:
    """Return a cached read-only engine for the SQLite database.

    When *db_path* is ``None`` (the default), the path is derived from
    ``settings.DATABASE_URL`` so that the read-only engine always targets
    the same file as the main application engine — including Docker
    deployments where the database lives outside the working directory.

    The ``mode=ro`` URI flag makes the SQLite driver reject any write
    at the engine level — this is the last line of defense if the
    sqlglot guardrail is bypassed.

    Args:
        db_path: Explicit path to the SQLite database file.  Pass a value
            only in tests; production code should use the default ``None``.

    Returns:
        A SQLAlchemy ``Engine`` configured in read-only mode.

    Raises:
        FileNotFoundError: If the resolved database file does not exist.
        ValueError: If ``DATABASE_URL`` is not a SQLite URL and no explicit
            *db_path* was provided.
    """
    from app.config import settings  # local import avoids circular dependency at module load

    path = db_path if db_path is not None else _path_from_database_url(settings.DATABASE_URL)
    resolved = Path(path).resolve()
    if not resolved.exists():
        raise FileNotFoundError(f"Database file not found: {resolved}")

    uri = f"sqlite:///file:{resolved}?mode=ro&uri=true"
    return create_engine(uri, connect_args={"uri": True})
