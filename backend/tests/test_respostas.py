import uuid

from app.models.usuario import Usuario
from app.security import create_access_token, get_password_hash
from tests.conftest import (
    criar_avaliacao,
    criar_consumidor,
    criar_pedido_com_item,
    criar_vendedor,
)

PRODUTO_BASE = {
    "nome_produto": "Tênis de Resposta",
    "categoria_produto": "calcados",
    "peso_produto_gramas": 500.0,
    "comprimento_centimetros": 30.0,
    "altura_centimetros": 15.0,
    "largura_centimetros": 10.0,
}


def criar_produto(client, admin_headers, dados=None):
    return client.post("/api/produtos/", json=dados or PRODUTO_BASE, headers=admin_headers)


def test_responder_avaliacao_sucesso(client, admin_headers, db):
    r = criar_produto(client, admin_headers)
    assert r.status_code == 201
    id_produto = r.json()["id_produto"]

    id_consumidor = criar_consumidor(db)
    id_vendedor = criar_vendedor(db)
    id_pedido = criar_pedido_com_item(db, id_produto, id_consumidor, id_vendedor)
    id_avaliacao = criar_avaliacao(db, id_pedido, nota=5, titulo="Ótimo", comentario="Excelente")

    payload = {"resposta": "Obrigado pelo feedback!"}
    r2 = client.post(
        f"/api/produtos/avaliacoes/{id_avaliacao}/resposta", json=payload, headers=admin_headers
    )
    assert r2.status_code == 200
    body = r2.json()
    assert body["resposta_admin"] == payload["resposta"]
    assert body["autor_resposta"] == "admin"
    assert body["data_resposta"] is not None


def test_responder_avaliacao_nao_encontrada(client, admin_headers):
    payload = {"resposta": "Obrigado"}
    r = client.post(
        "/api/produtos/avaliacoes/invalid_id/resposta", json=payload, headers=admin_headers
    )
    assert r.status_code == 404


def test_responder_avaliacao_proibido_para_nao_admin(client, db, admin_headers):
    r = criar_produto(client, admin_headers)
    assert r.status_code == 201
    id_produto = r.json()["id_produto"]

    id_consumidor = criar_consumidor(db)
    id_vendedor = criar_vendedor(db)
    id_pedido = criar_pedido_com_item(db, id_produto, id_consumidor, id_vendedor)
    id_avaliacao = criar_avaliacao(db, id_pedido, nota=4)

    username = f"user_{uuid.uuid4().hex[:8]}"
    user = Usuario(
        id_usuario=uuid.uuid4().hex,
        username=username,
        hashed_password=get_password_hash("1234"),
        is_admin=False,
    )
    db.add(user)
    db.commit()

    token = create_access_token({"sub": user.username})
    user_headers = {"Authorization": f"Bearer {token}"}

    payload = {"resposta": "Tentativa indevida"}
    r2 = client.post(
        f"/api/produtos/avaliacoes/{id_avaliacao}/resposta", json=payload, headers=user_headers
    )
    assert r2.status_code == 403


def test_deletar_resposta_avaliacao_sucesso(client, admin_headers, db):
    r = criar_produto(client, admin_headers)
    id_produto = r.json()["id_produto"]

    id_consumidor = criar_consumidor(db)
    id_vendedor = criar_vendedor(db)
    id_pedido = criar_pedido_com_item(db, id_produto, id_consumidor, id_vendedor)
    id_avaliacao = criar_avaliacao(db, id_pedido, nota=5)

    payload = {"resposta": "Deletar me!"}
    client.post(
        f"/api/produtos/avaliacoes/{id_avaliacao}/resposta", json=payload, headers=admin_headers
    )

    r2 = client.delete(f"/api/produtos/avaliacoes/{id_avaliacao}/resposta", headers=admin_headers)
    assert r2.status_code == 200
    body = r2.json()
    assert body["resposta_admin"] is None
    assert body["autor_resposta"] is None
    assert body["data_resposta"] is None


# --- Testes de invalidação de cache ---


def test_cache_invalida_apos_responder_avaliacao(client, admin_headers, db):
    id_produto = criar_produto(client, admin_headers).json()["id_produto"]
    id_consumidor = criar_consumidor(db)
    id_vendedor = criar_vendedor(db)
    id_pedido = criar_pedido_com_item(db, id_produto, id_consumidor, id_vendedor)
    id_avaliacao = criar_avaliacao(db, id_pedido, nota=5, titulo="Ótimo", comentario="Excelente")

    r1 = client.get(f"/api/produtos/{id_produto}/avaliacoes", headers=admin_headers)
    assert r1.json()["avaliacoes"][0]["resposta_admin"] is None

    client.post(
        f"/api/produtos/avaliacoes/{id_avaliacao}/resposta",
        json={"resposta": "Obrigado!"},
        headers=admin_headers,
    )

    r2 = client.get(f"/api/produtos/{id_produto}/avaliacoes", headers=admin_headers)
    assert r2.json()["avaliacoes"][0]["resposta_admin"] == "Obrigado!"


def test_cache_invalida_apos_deletar_resposta(client, admin_headers, db):
    id_produto = criar_produto(client, admin_headers).json()["id_produto"]
    id_consumidor = criar_consumidor(db)
    id_vendedor = criar_vendedor(db)
    id_pedido = criar_pedido_com_item(db, id_produto, id_consumidor, id_vendedor)
    id_avaliacao = criar_avaliacao(db, id_pedido, nota=4)

    client.post(
        f"/api/produtos/avaliacoes/{id_avaliacao}/resposta",
        json={"resposta": "Resposta inicial"},
        headers=admin_headers,
    )

    r1 = client.get(f"/api/produtos/{id_produto}/avaliacoes", headers=admin_headers)
    assert r1.json()["avaliacoes"][0]["resposta_admin"] == "Resposta inicial"

    client.delete(f"/api/produtos/avaliacoes/{id_avaliacao}/resposta", headers=admin_headers)

    r2 = client.get(f"/api/produtos/{id_produto}/avaliacoes", headers=admin_headers)
    assert r2.json()["avaliacoes"][0]["resposta_admin"] is None
