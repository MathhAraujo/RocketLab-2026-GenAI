# Atividade GenAI — Rocket Lab 2026

Entrega da **Atividade GenAI** do Rocket Lab 2026: agente **Text-to-SQL** capaz de responder perguntas em linguagem natural sobre o banco de dados de um e-commerce, gerando tabelas, gráficos e comentários analíticos.

> Este documento é o ponto de partida para avaliar a atividade. Para informações sobre a aplicação fullstack completa (catálogo, autenticação, etc.), veja [`README.md`](./README.md).

---

## 1. Aderência aos requisitos da atividade

| Requisito do enunciado | Entrega |
|---|---|
| Framework de agentes à escolha | **PydanticAI** (`pydantic-ai`) |
| Modelo | **Gemini 2.5 Flash** (via `google-genai`) |
| Linguagem | **Python 3.11+** |
| Entregável | **Módulo de backend FastAPI** + frontend React para interface visual |
| README de passo-a-passo | Este arquivo + [`README.md`](./README.md) |
| Banco SQLite (`banco.db`) | Carregado a partir dos CSVs oficiais em `backend/data/` (`dim_*.csv`, `fat_*.csv`) para `backend/database.db` (ou volume Docker) via `seed.py` |

### Categorias de perguntas suportadas (exemplos testados)

- **Vendas e receita** — *Top 10 produtos mais vendidos; receita total por categoria*
- **Entrega e logística** — *Quantidade de pedidos por status; % entregues no prazo por estado*
- **Satisfação e avaliações** — *Média de avaliação geral; média por vendedor (top 10)*
- **Consumidores** — *Estados com maior volume e ticket médio; estados com maior atraso*
- **Vendedores e produtos** — *Produtos mais vendidos por estado; categorias com mais avaliação negativa*

A tela `/assistente` traz uma barra de **perguntas de exemplo** cobrindo cada categoria.

### Extras implementados (seção de criatividade do enunciado)

- **Guardrails de segurança**
  - `sqlglot` valida que só `SELECT` é executado (bloqueia `INSERT`, `UPDATE`, `DELETE`, `DROP`, etc.)
  - Tabela `usuarios` (senhas) é **blacklisted**
  - `LIMIT 1000` injetado automaticamente em toda query
  - Engine SQLite aberto em modo read-only (`mode=ro`) — última camada de defesa
- **Interface visual** — dashboard React com tabelas formatadas (monetário, float, inteiro) e gráficos (bar, line, pie, area, scatter) renderizados via `recharts`
- **Anonimização de PII** — toggle na interface mascara nomes, CEP e comentários antes de enviar ao LLM
- **Agente de insight analítico** — segundo agente Gemini produz um comentário curto (2–4 frases) ancorado nos dados retornados, com regras anti-alucinação
- **Retry com auto-correção** — falhas transitórias disparam até 3 tentativas, injetando o erro anterior no contexto
- **Controle de acesso** — apenas usuários `admin` podem fazer perguntas; `viewer` visualiza histórico/sugestões
- **Histórico local** — consultas ficam salvas no `localStorage` do navegador, com replay completo

---

## 2. Stack técnica

| Camada | Tecnologia |
|---|---|
| Agente | PydanticAI + `google-genai` SDK |
| Modelo | `gemini-2.5-flash` |
| Backend | FastAPI 0.115 + SQLAlchemy 2.0 |
| Banco | SQLite (`database.db`) |
| Validação SQL | `sqlglot` (AST parsing + hardening) |
| Frontend | React 19 + Vite + TypeScript + Tailwind 4 + Recharts |
| Testes | `pytest` + `httpx` (backend) |
| Lint/Type | `ruff` + `mypy --strict` (backend) / ESLint + TypeScript + Prettier (frontend) |

Arquitetura resumida (backend):

```
router/assistente.py
    └── services/assistente_service.py   ← orquestrador
          ├── agents/sql_agent.py        ← gera SQL (Gemini)
          ├── services/sql_guardrail.py  ← valida e endurece
          ├── services/readonly_db.py    ← engine mode=ro
          ├── services/anonymizer.py     ← PII masking
          └── agents/insight_agent.py    ← comentário analítico
```

---

## 3. Pré-requisitos

Para executar, você vai precisar de **uma** das duas opções:

- **Com Docker**: apenas Docker Desktop (ou Docker Engine + Compose v2).
- **Sem Docker**: Python **3.11+** e Node.js **20+**.

Em ambos os casos, **uma chave de API do Gemini** é obrigatória para usar o assistente (sem ela, os endpoints de análise retornam HTTP 503).

---

## 4. Obtendo a chave do Gemini

1. Acesse [Google AI Studio — API keys](https://aistudio.google.com/app/apikey).
2. Clique em **"Create API key"** e copie o valor gerado.
3. Guarde o valor — você vai colá-lo na variável `GOOGLE_API_KEY` na próxima seção.

> A chave do plano gratuito já é suficiente para testar a atividade. O sistema trata automaticamente erros de rate limit (429) e quota (503).

---

## 5. Configurando as variáveis de ambiente

A aplicação lê variáveis de dois arquivos, dependendo de como você roda:

| Arquivo | Quando é lido | Para quê |
|---|---|---|
| `backend/.env` | Execução **sem Docker** (Uvicorn local) | Configurações do backend local |
| `.env` (raiz do repo) | Execução **com Docker** (`docker compose`) | Passar `GOOGLE_API_KEY` para o container |

### 5.1. Sem Docker — `backend/.env`

O repositório traz um template em `backend/.env.example`. Copie-o e preencha:

```bash
# Na raiz do repositório
cp backend/.env.example backend/.env
```

Depois edite `backend/.env`:

```dotenv
# URL de conexão com o banco SQLite (não precisa alterar em dev)
DATABASE_URL=sqlite:///./database.db

# Segredo para assinatura de JWT. Em dev pode deixar em branco (será gerado aleatoriamente a cada start).
# Em produção, use um valor longo e aleatório:  python -c "import secrets; print(secrets.token_hex(32))"
JWT_SECRET=

# OBRIGATÓRIA para o assistente. Cole a chave obtida em https://aistudio.google.com/app/apikey
GOOGLE_API_KEY=cole-sua-chave-aqui
```

### 5.2. Com Docker — `.env` (na raiz do repo)

O `docker-compose.yml` referencia `${GOOGLE_API_KEY}`, que o Docker Compose lê **automaticamente** de um `.env` na raiz do repositório. Crie esse arquivo:

```bash
# Na raiz do repositório, crie .env com o conteúdo:
echo "GOOGLE_API_KEY=cole-sua-chave-aqui" > .env
```

Ou, em sistemas onde `echo` não aceite `>` (alguns shells Windows), crie o arquivo manualmente com o editor de sua preferência.

> **Importante**: o arquivo `.env` da raiz **não** é versionado (está no `.gitignore`). Não commite a chave.

---

## 6. Executando com Docker (recomendado)

```bash
# 1. (se ainda não fez) criar .env na raiz com GOOGLE_API_KEY — veja seção 5.2
# 2. Build + subir
docker compose up --build
```

O container de backend executa automaticamente:
1. `alembic upgrade head` (cria as tabelas)
2. `python seed.py` (carrega os CSVs em `backend/data/`)
3. `uvicorn` na porta 8000

Quando os logs indicarem que o backend e o frontend estão prontos, acesse:

| Serviço | URL |
|---|---|
| Interface do assistente | http://localhost:5173/assistente |
| Login | http://localhost:5173 |
| API (Swagger) | http://localhost:8000/docs |
| Health-check do assistente | http://localhost:8000/api/assistente/saude |

Para parar:

```bash
docker compose down
```

Para limpar o volume com o banco (reset completo):

```bash
docker compose down -v
```

---

## 7. Executando sem Docker

### 7.1. Backend

Em um terminal, a partir da raiz do repositório:

```bash
cd backend

# 1. Ambiente virtual
python -m venv .venv

# Linux / macOS
source .venv/bin/activate
# Windows (PowerShell)
.venv\Scripts\Activate.ps1
# Windows (cmd / Git Bash)
.venv\Scripts\activate

# 2. Dependências
pip install -r requirements.txt

# 3. Variáveis de ambiente (se ainda não fez — ver seção 5.1)
cp .env.example .env
# edite backend/.env e preencha GOOGLE_API_KEY

# 4. Criar e popular o banco
alembic upgrade head
python seed.py

# 5. Subir o servidor
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 7.2. Frontend

Em **outro terminal**, a partir da raiz:

```bash
cd frontend
npm install
npm run dev
```

Acesse http://localhost:5173/assistente.

---

## 8. Primeiro uso

1. Abra http://localhost:5173 e clique em **"Criar uma nova conta"**.
2. Selecione o perfil **Administrador** (o perfil `viewer` não pode enviar perguntas, apenas ver o histórico).
3. Faça login e acesse a aba **Assistente** no menu (ou vá direto a http://localhost:5173/assistente).
4. Use as **perguntas de exemplo** ou escreva uma pergunta livre em português.

### Perguntas que validam cada categoria do enunciado

Cole essas perguntas no assistente para validar a cobertura da atividade:

1. `Top 10 produtos mais vendidos`
2. `Qual a receita total por categoria de produto?`
3. `Quantidade de pedidos por status`
4. `Qual o percentual de pedidos entregues no prazo por estado?`
5. `Qual a média de avaliação dos pedidos?`
6. `Top 10 vendedores com maior média de avaliação`
7. `Quais estados têm maior volume de pedidos e maior ticket médio?`
8. `Quais estados têm maior atraso médio na entrega?`
9. `Quais categorias de produto têm maior taxa de avaliação negativa?`
10. `Produtos mais vendidos no estado de São Paulo`

---

## 9. Verificando que está tudo funcionando

Rode o health-check:

```bash
curl http://localhost:8000/api/assistente/saude
```

Resposta esperada:

```json
{
  "status": "ok",
  "gemini_configurado": true,
  "banco_acessivel": true
}
```

Se `gemini_configurado` vier `false`, a `GOOGLE_API_KEY` não foi carregada — reveja a seção 5.

---

## 10. Rodando os testes

```bash
cd backend
# com o venv ativo
pytest tests/ -v
```

Os testes usam um SQLite em memória e **não** chamam o Gemini real — o agente é mockado. Cobrem:

- `test_sql_guardrail.py` — bloqueio de DML/DDL, blacklist `usuarios`, injeção de LIMIT
- `test_anonymizer.py` — mascaramento determinístico e reversibilidade do mapping
- `test_readonly_db.py` — tentativa de escrita contra engine read-only
- `test_retry.py` — loop de retry com auto-correção
- `test_agents.py` — contrato do agente (com mock)
- `test_assistente_endpoint.py` — happy path do endpoint

---

## 11. Estrutura relevante para a atividade

```
backend/
├── app/
│   ├── agents/
│   │   ├── sql_agent.py         # Gera SQL a partir de linguagem natural
│   │   ├── insight_agent.py     # Produz comentário analítico
│   │   └── schema_context.py    # Schema do banco injetado no prompt
│   ├── services/
│   │   ├── assistente_service.py  # Orquestrador
│   │   ├── sql_guardrail.py       # Valida SELECT-only + LIMIT
│   │   ├── anonymizer.py          # Mascaramento de PII
│   │   └── readonly_db.py         # Engine SQLite mode=ro
│   ├── routers/assistente.py    # Endpoints /perguntar e /saude
│   └── schemas/assistente.py    # Request/response Pydantic
├── data/                        # CSVs originais da atividade (dim_*, fat_*)
├── tests/                       # pytest
└── seed.py                      # Popula o banco a partir dos CSVs

frontend/
└── src/
    ├── pages/AssistentePage.tsx          # Página principal do assistente
    └── components/assistente/            # Componentes (gráficos, tabela, toggle…)
```

---

## 12. Solução de problemas rápidos

| Sintoma | Causa provável | Solução |
|---|---|---|
| `POST /api/assistente/perguntar` retorna 503 | `GOOGLE_API_KEY` ausente | Ver seção 5 |
| `gemini_configurado: false` no `/saude` | `.env` não carregado | Reinicie o uvicorn; em Docker, `docker compose down && up` |
| Erro 429 "Muitas requisições" | Rate limit do plano gratuito | Aguarde 1 minuto e tente de novo |
| Banco vazio (nenhum dado) | `seed.py` não rodou | `python seed.py` (sem Docker) ou recriar volume (`docker compose down -v`) |
| Frontend não conecta ao backend | CORS ou `VITE_API_URL` | Verifique que o backend está em `:8000` e que a origem `:5173` está em `ALLOWED_ORIGINS` |

---

## 13. Não-objetivos (escopo da atividade)

Para manter a entrega focada, **não foram implementados**:

- Chat conversacional (o enunciado dispensa explicitamente)
- Exportação de resultados (CSV/Excel)
- Edição manual do SQL gerado
- Streaming da resposta do LLM
- Autenticação SSO / OAuth
- Deploy em nuvem
