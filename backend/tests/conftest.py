import uuid
from collections.abc import Generator
from datetime import datetime
from typing import Any

import pytest
from fastapi.testclient import TestClient
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models
from app.agents.insight_agent import InsightResult
from app.agents.sql_agent import SqlGenerationResult
from app.database import Base, get_db
from app.main import app, custom_key_builder
from app.models.avaliacao_pedido import AvaliacaoPedido
from app.models.consumidor import Consumidor
from app.models.item_pedido import ItemPedido
from app.models.pedido import Pedido
from app.models.produto import Produto
from app.models.usuario import Usuario
from app.models.vendedor import Vendedor
from app.routers.assistente import get_assistente_engine
from app.security import get_password_hash


@pytest.fixture(autouse=True)
def reset_cache():
    FastAPICache.init(InMemoryBackend(), prefix="fastapi-cache", key_builder=custom_key_builder)
    yield


@pytest.fixture
def _engine() -> Engine:
    """In-memory SQLite engine shared by the session and the assistente service."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def db(_engine: Engine) -> Generator[Any, None, None]:
    session_factory = sessionmaker(bind=_engine)
    sessao = session_factory()
    yield sessao
    sessao.close()


def _seed_admin(db):
    admin = Usuario(
        id_usuario=uuid.uuid4().hex,
        username="admin",
        hashed_password=get_password_hash("admin"),
        is_admin=True,
    )
    db.add(admin)
    db.commit()
    return admin


def _seed_user(db):
    user = Usuario(
        id_usuario=uuid.uuid4().hex,
        username="visitante",
        hashed_password=get_password_hash("1234"),
        is_admin=False,
    )
    db.add(user)
    db.commit()
    return user


@pytest.fixture
def client(db):
    _seed_admin(db)

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def admin_headers(client):
    r = client.post("/api/auth/login", json={"username": "admin", "password": "admin"})
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def user_client(db):
    _seed_admin(db)
    _seed_user(db)

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def user_headers(user_client):
    r = user_client.post("/api/auth/login", json={"username": "visitante", "password": "1234"})
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def criar_consumidor(db) -> str:
    id_consumidor = uuid.uuid4().hex
    db.add(
        Consumidor(
            id_consumidor=id_consumidor,
            nome_consumidor="Consumidor Teste",
            prefixo_cep="01310",
            cidade="São Paulo",
            estado="SP",
        )
    )
    db.commit()
    return id_consumidor


def criar_vendedor(db) -> str:
    id_vendedor = uuid.uuid4().hex
    db.add(
        Vendedor(
            id_vendedor=id_vendedor,
            nome_vendedor="Vendedor Teste",
            prefixo_cep="01310",
            cidade="São Paulo",
            estado="SP",
        )
    )
    db.commit()
    return id_vendedor


def criar_pedido_com_item(
    db,
    id_produto: str,
    id_consumidor: str,
    id_vendedor: str,
    preco: float = 100.0,
    status: str = "entregue",
) -> str:
    id_pedido = uuid.uuid4().hex
    db.add(
        Pedido(
            id_pedido=id_pedido,
            id_consumidor=id_consumidor,
            status=status,
        )
    )
    db.add(
        ItemPedido(
            id_pedido=id_pedido,
            id_item=1,
            id_produto=id_produto,
            id_vendedor=id_vendedor,
            preco_BRL=preco,
            preco_frete=10.0,
        )
    )
    db.commit()
    return id_pedido


# ---------------------------------------------------------------------------
# Fixtures for /api/assistente endpoint tests (TASK-15)
# ---------------------------------------------------------------------------

_CANNED_SQL = "SELECT nome_produto, total_vendas FROM produtos ORDER BY total_vendas DESC LIMIT 10"
_CANNED_ROWS: list[list[Any]] = [
    ["Produto A", 100],
    ["Produto B", 80],
    ["Produto C", 60],
]
_CANNED_COLUMNS = ["nome_produto", "total_vendas"]


def _seed_assistente_data(db: Any) -> None:
    """Seed minimal produto row so the read-only engine has data to return."""
    db.add(
        Produto(
            id_produto=uuid.uuid4().hex,
            nome_produto="Produto A",
            categoria_produto="Eletrônicos",
            total_vendas=100,
        )
    )
    db.commit()


@pytest.fixture
def test_db(db: Any) -> Any:
    """In-memory SQLite seeded with admin, viewer, and minimal e-commerce data."""
    _seed_admin(db)
    _seed_user(db)
    _seed_assistente_data(db)
    return db


@pytest.fixture
def admin_client(test_db: Any, _engine: Engine) -> Generator[TestClient, None, None]:
    """TestClient with DB and read-only engine overridden; caller must obtain auth headers."""

    def _override() -> Generator[Any, None, None]:
        yield test_db

    app.dependency_overrides[get_db] = _override
    app.dependency_overrides[get_assistente_engine] = lambda: _engine
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def viewer_client(test_db: Any, _engine: Engine) -> Generator[TestClient, None, None]:
    """TestClient with DB and read-only engine overridden; caller must obtain auth headers."""

    def _override() -> Generator[Any, None, None]:
        yield test_db

    app.dependency_overrides[get_db] = _override
    app.dependency_overrides[get_assistente_engine] = lambda: _engine
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def admin_token(admin_client: TestClient) -> str:
    """JWT token for the admin user."""
    r = admin_client.post("/api/auth/login", json={"username": "admin", "password": "admin"})
    return str(r.json()["access_token"])


@pytest.fixture
def viewer_token(viewer_client: TestClient) -> str:
    """JWT token for the viewer user."""
    r = viewer_client.post("/api/auth/login", json={"username": "visitante", "password": "1234"})
    return str(r.json()["access_token"])


@pytest.fixture
def mock_sql_agent(monkeypatch: pytest.MonkeyPatch) -> SqlGenerationResult:
    """Patch gerar_sql with a canned successful result (no Gemini call)."""
    result = SqlGenerationResult(
        sql=_CANNED_SQL,
        explicacao_seca="Os 10 produtos com maior volume de vendas.",
        sugestao_grafico="bar",
        grafico_config={"eixo_x": "nome_produto", "eixo_y": "total_vendas"},
        forcar_tabela=True,
        eh_off_topic=False,
    )

    async def _fake(*args: Any, **kwargs: Any) -> SqlGenerationResult:
        return result

    monkeypatch.setattr("app.agents.sql_agent.gerar_sql", _fake)
    return result


@pytest.fixture
def mock_insight_agent(monkeypatch: pytest.MonkeyPatch) -> InsightResult:
    """Patch gerar_insight with a canned result (no Gemini call)."""
    result = InsightResult(
        explicacao_analitica="Produto A lidera com 100 vendas, seguido por B (80) e C (60)."
    )

    async def _fake(*args: Any, **kwargs: Any) -> InsightResult:
        return result

    monkeypatch.setattr("app.agents.insight_agent.gerar_insight", _fake)
    return result


def criar_avaliacao(
    db,
    id_pedido: str,
    nota: int,
    titulo: str | None = None,
    comentario: str | None = None,
) -> str:
    id_avaliacao = uuid.uuid4().hex
    db.add(
        AvaliacaoPedido(
            id_avaliacao=id_avaliacao,
            id_pedido=id_pedido,
            avaliacao=nota,
            titulo_comentario=titulo,
            comentario=comentario,
            data_comentario=datetime.now(),
        )
    )
    db.commit()
    return id_avaliacao
