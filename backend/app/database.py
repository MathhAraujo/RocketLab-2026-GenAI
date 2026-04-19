"""Engine SQLAlchemy, fábrica de sessões e base declarativa para os modelos ORM."""

from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings

connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Classe base para todos os modelos ORM SQLAlchemy."""


def get_db() -> Generator[Session, None, None]:
    """Fornecer uma sessão de banco de dados e garantir seu fechamento ao final."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
