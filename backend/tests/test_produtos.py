PRODUTO_BASE = {
    "nome_produto": "Tênis de Teste",
    "categoria_produto": "calcados",
    "peso_produto_gramas": 500.0,
    "comprimento_centimetros": 30.0,
    "altura_centimetros": 15.0,
    "largura_centimetros": 10.0,
}

def criar(client, dados=None):
    return client.post("/produtos/", json=dados or PRODUTO_BASE)


def test_listar_vazio(client):
    r = client.get("/produtos/")
    assert r.status_code == 200
    assert r.json() == {"total": 0, "items": []}


def test_criar_produto(client):
    r = criar(client)
    assert r.status_code == 201
    body = r.json()
    assert body["nome_produto"] == PRODUTO_BASE["nome_produto"]
    assert "id_produto" in body


def test_listar_retorna_produto_criado(client):
    criar(client)
    r = client.get("/produtos/")
    assert r.json()["total"] == 1


def test_busca_por_nome(client):
    criar(client)
    r = client.get("/produtos/?busca=Tênis")
    assert r.json()["total"] == 1
    r = client.get("/produtos/?busca=inexistente")
    assert r.json()["total"] == 0


def test_filtro_por_categoria(client):
    criar(client)
    r = client.get("/produtos/?categoria=calcados")
    assert r.json()["total"] == 1
    r = client.get("/produtos/?categoria=outra")
    assert r.json()["total"] == 0


def test_paginacao(client):
    for i in range(5):
        criar(client, {**PRODUTO_BASE, "nome_produto": f"Produto {i}"})
    r = client.get("/produtos/?skip=0&limit=2")
    body = r.json()
    assert body["total"] == 5
    assert len(body["items"]) == 2


def test_obter_produto(client):
    id_ = criar(client).json()["id_produto"]
    r = client.get(f"/produtos/{id_}")
    assert r.status_code == 200
    body = r.json()
    assert body["id_produto"] == id_
    assert "vendas" in body
    assert "avaliacoes" in body


def test_obter_produto_inexistente(client):
    r = client.get("/produtos/id-que-nao-existe")
    assert r.status_code == 404


def test_atualizar_produto(client):
    id_ = criar(client).json()["id_produto"]
    r = client.put(f"/produtos/{id_}", json={"nome_produto": "Novo Nome"})
    assert r.status_code == 200
    assert r.json()["nome_produto"] == "Novo Nome"


def test_atualizar_body_vazio_retorna_422(client):
    id_ = criar(client).json()["id_produto"]
    r = client.put(f"/produtos/{id_}", json={})
    assert r.status_code == 422


def test_deletar_produto(client):
    id_ = criar(client).json()["id_produto"]
    r = client.delete(f"/produtos/{id_}")
    assert r.status_code == 204
    r = client.get(f"/produtos/{id_}")
    assert r.status_code == 404


def test_listar_categorias(client):
    criar(client)
    r = client.get("/produtos/categorias")
    assert r.status_code == 200
    assert "calcados" in r.json()