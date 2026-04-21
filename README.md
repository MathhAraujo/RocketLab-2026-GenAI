# Implementação Text-to-SQL

Agente inteligente integrado ao Sistema de Gerenciamento de E-Commerce. A funcionalidade permite que usuários realizem consultas de leitura no banco de dados através de perguntas em linguagem natural (Text-to-SQL), gerando como resultado tabelas estruturadas, gráficos visuais e comentários analíticos.

> Este documento cobre apenas o que é específico desta integração. A documentação da aplicação fullstack de base (catálogo, autenticação, estrutura geral, Docker, acesso pelo celular, variáveis de ambiente do backend/frontend, execução de testes) está em [`README-DEV.md`](./README-DEV.md) - leia-o antes.

---

## 1. Aderência aos requisitos da atividade

| Requisito do enunciado | Entrega |
|---|---|
| Framework de agentes à escolha | **PydanticAI** (`pydantic-ai`) |
| Modelo | **Gemini 2.5 Flash** (via `google-genai`) |
| Linguagem | **Python 3.11+** |
| Entregável | **Módulo de backend FastAPI** + frontend React para interface visual |
| Banco SQLite (`banco.db`) | Carregado a partir dos CSVs oficiais em `backend/data/` (`dim_*.csv`, `fat_*.csv`) para `backend/database.db` (ou volume Docker) via `seed.py` |

### Perguntas Sugeridas

A tela `/assistente` traz uma barra de perguntas sugeridas com acesso de um clique às consultas abaixo (definidas em `frontend/src/components/assistente/SampleQuestions.tsx`):

1. Top 10 produtos mais vendidos
2. Qual a distribuição de pedidos por status?
3. Quais categorias de produto têm maior receita total?
4. Qual a média de avaliação dos pedidos por categoria?
5. Quantos pedidos foram feitos por estado?
6. Quais são os 5 vendedores com maior volume de vendas?
7. Qual o percentual de pedidos entregues no prazo?
8. Quais produtos têm avaliação média abaixo de 3?
9. Qual a receita total por mês?
10. Qual a receita média por pedido agrupada por estado?

### Extras implementados

- **Guardrails de segurança**
  - `sqlglot` valida que só `SELECT` é executado (bloqueia `INSERT`, `UPDATE`, `DELETE`, `DROP`, etc.)
  - Tabela `usuarios` é **blacklisted**
  - `LIMIT 1000` injetado automaticamente em toda query
  - Engine SQLite aberto em modo read-only (`mode=ro`) - última camada de defesa
- **Anonimização de PII (apenas para o LLM)** - toggle na interface que mascara dados sensíveis **exclusivamente no payload enviado ao agente de insight**. As tabelas e gráficos exibidos ao usuário sempre mostram os valores originais do banco; só o texto analítico gerado pelo Gemini é produzido em cima dos dados mascarados (`backend/app/services/assistente_service.py:222-226`). As transformações aplicadas por coluna são:
  - `nome_consumidor` → `Consumidor_{hash6}` (hash SHA-1 truncado em 6 caracteres, determinístico)
  - `nome_vendedor` → `Vendedor_{hash6}`
  - `autor_resposta` → `Usuario_{hash6}`
  - `prefixo_cep` → dois primeiros dígitos + `***` (ex.: `22***`)
  - `comentario` e `titulo_comentario` → truncados em 40 caracteres e com qualquer sequência numérica de 3+ dígitos substituída por `***`
  - Um mapeamento reverso dos hashes de nomes é devolvido junto à resposta (`traducao_anonimizacao`) como legenda para o usuário decodificar os tokens que aparecerem no insight
- **Interface visual** - dashboard React com tabelas formatadas (monetário, float, inteiro) e gráficos (bar, line, pie, area, scatter) renderizados via `recharts`
- **Agente de insight analítico** - segundo agente Gemini produz um comentário curto (2-4 frases) ancorado nos dados retornados, com regras anti-alucinação
- **Retry com auto-correção** - falhas transitórias disparam até 3 tentativas, injetando o erro anterior no contexto
- **Controle de acesso** - apenas usuários `admin` podem fazer perguntas; `viewer` visualiza histórico/sugestões
- **Histórico local** - consultas ficam salvas no `localStorage` do navegador, com replay completo

---

## 2. Stack adicionada nesta entrega

Além da stack descrita em [`README-DEV.md`](./README-DEV.md), a feature do assistente adiciona:

| Camada | Tecnologia |
|---|---|
| Framework de agentes | `pydantic-ai` |
| SDK do modelo | `google-genai` |
| Modelo | `gemini-2.5-flash` |
| Validação/parsing de SQL | `sqlglot` |
| Gráficos no frontend | `recharts` |

Arquitetura resumida:

```
router/assistente.py
    └── services/assistente_service.py   ← orquestrador
          ├── agents/sql_agent.py        ← gera SQL (Gemini)
          ├── services/sql_guardrail.py  ← valida e endurece
          ├── services/readonly_db.py    ← engine mode=ro
          ├── services/anonymizer.py     ← PII masking
          └── agents/insight_agent.py    ← comentário analítico
```

### 2.1. Estrutura relevante para esta entrega

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
└── data/                        # CSVs originais da atividade (dim_*, fat_*)

frontend/src/
├── pages/AssistentePage.tsx              # Página principal do assistente
└── components/assistente/                # Componentes (gráficos, tabela, toggle…)
```

---

## 3. Clonando o repositório

```bash
git clone <url-do-repositorio>
cd RocketLab-2026-GenAI
```

---

## 4. Obtendo a chave do Gemini

Uma **chave de API do Gemini é obrigatória** para usar o assistente. Sem ela, o endpoint `/api/assistente/perguntar` retorna HTTP 503.

1. Acesse [Google AI Studio - API keys](https://aistudio.google.com/app/apikey).
2. Clique em **"Create API key"** e copie o valor gerado.
3. Guarde o valor - você vai colá-lo no `.env` da aplicação na próxima seção.

> A chave do plano gratuito já é suficiente para testar a atividade. O sistema trata automaticamente erros de rate limit (429) e quota (503).

---

## 5. Configurando variáveis de ambiente

A aplicação requer algumas variáveis de ambiente para funcionar confiavelmente (como a chave do Gemini e o segredo do JWT). O repositório fornece um arquivo de exemplo localizado em `backend/.env.example`.

Para começar, crie uma cópia chamada `.env`. Dependendo da sua abordagem de execução (com Docker ou local), o local onde criar sua cópia muda:

```bash
# Se for rodar SEM Docker (crie dentro da pasta backend/):
cp backend/.env.example backend/.env

# Se for rodar COM Docker (crie na raiz do repositório):
cp backend/.env.example .env
```

Após criar o seu novo `.env`, abra-o no seu editor de preferência. As duas variáveis principais que exigem preenchimento manual são:

```dotenv
GOOGLE_API_KEY=<API_KEY>
JWT_SECRET=<64_Char_String>
```

- `GOOGLE_API_KEY`: Cole aqui a chave recém-gerada no Google AI Studio (passo 4).
- `JWT_SECRET`: Digite ou gere uma string aleatória de exatamente 64 caracteres. Em desenvolvimento, **este campo pode ser deixado vazio** (nesse caso, gerar-se-á uma efêmera na primeira chamada), porém alertamos que isso invalidará logins a cada "reinício de container/servidor". Se preferir gerar uma de 64 caracteres rapidamente no terminal para preencher: `python -c 'import secrets; print(secrets.token_hex(32))'`.
- As demais variáveis providenciadas pelo `.env.example` (como a `DATABASE_URL` e `ALLOWED_ORIGINS`) já possuem valores preenchidos na arquitetura ideal para `localhost` e seguem os conformes estabelecidos no original [`README-DEV.md`](./README-DEV.md).

---

## 6. Primeira execução

### 6.1. Sem Docker

**Pré-requisitos:** Python **3.11+** e Node.js **20+**.

#### Backend

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

# 3. Variáveis de ambiente (ver seção 5)
# (Assumindo que você já copiou e preencheu o backend/.env)

# 4. Criar e popular o banco (só na primeira execução)
alembic upgrade head
python seed.py

# 5. Subir o servidor
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Frontend

Em **outro terminal**, a partir da raiz:

```bash
cd frontend
npm install
npm run dev
```

### 6.2. Com Docker (Recomendado)

**Pré-requisito:** Docker Desktop (ou Docker Engine + Compose v2) instalado.

```bash
# 1. Garantir que o ambiente possua variáveis configuráveis (ver seção 5)
# (Assumindo que você já copiou e preencheu as chaves no ./env da raiz)

# 2. Build + subir
docker compose up --build
```

O container de backend executa automaticamente, nesta ordem:

1. `alembic upgrade head` (cria as tabelas)
2. `python seed.py` (carrega os CSVs em `backend/data/` - equivalente ao `banco.db` mencionado no enunciado)
3. `uvicorn` na porta 8000

Para parar:

```bash
docker compose down
```

Para limpar o volume com o banco (reset completo):

```bash
docker compose down -v
```

---

## 7. Verificando que está tudo funcionando

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

Se `gemini_configurado` vier `false`, a `GOOGLE_API_KEY` não foi carregada. Reveja a seção 5.

---

## 8. URLs da aplicação

| Serviço | URL |
|---|---|
| Interface do assistente | http://localhost:5173/assistente |
| Login | http://localhost:5173 |
| API (Swagger) | http://localhost:8000/docs |
| Health-check do assistente | http://localhost:8000/api/assistente/saude |

---

## 9. Primeiro uso do assistente

1. Crie uma conta com perfil **Administrador** (o perfil `viewer` não pode enviar perguntas, apenas ver histórico).
2. Acesse a aba **Assistente** no menu (ou vá direto a http://localhost:5173/assistente).
3. Use as **perguntas de exemplo** ou escreva uma pergunta livre em português.

---

## 10. Testes específicos desta entrega

A suíte de testes é executada conforme o `README-DEV.md`. Os testes novos desta entrega não chamam o Gemini real (o agente é mockado) e cobrem:

- `test_sql_guardrail.py` - bloqueio de DML/DDL, blacklist `usuarios`, injeção de `LIMIT`
- `test_anonymizer.py` - mascaramento determinístico e reversibilidade do mapping
- `test_readonly_db.py` - tentativa de escrita contra engine read-only
- `test_retry.py` - loop de retry com auto-correção
- `test_agents.py` - contrato do agente (com mock)
- `test_assistente_endpoint.py` - happy path do endpoint

---

## 11. Solução de problemas específicos do assistente

| Sintoma | Causa provável | Solução |
|---|---|---|
| `POST /api/assistente/perguntar` retorna 503 | `GOOGLE_API_KEY` ausente | Ver seção 5 |
| `gemini_configurado: false` no `/saude` | `.env` não carregado | Reinicie o uvicorn; em Docker, `docker compose down && up` |
| Erro 429 "Muitas requisições" | Rate limit do plano gratuito | Aguarde 1 minuto e tente de novo |
| Banco vazio (nenhum dado) | `seed.py` não rodou | `python seed.py` (sem Docker) ou recriar volume (`docker compose down -v`) |
