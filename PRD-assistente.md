# PRD — Assistente de Análise de Dados (`/assistente`)

> **Projeto:** RocketLab-2026-GenAI
> **Feature:** Dashboard com agente Text-to-SQL para análise de dados em linguagem natural
> **Versão do documento:** 1.2
> **Data:** 2026-04-19
> **Prazo de entrega:** 2026-04-22 18:00
> **Formato:** PRD híbrido (produto + técnico), otimizado para consumo por LLM e geração de backlog de implementação via Claude Code.

> **Changelog v1.1:**
> - Legibilidade de código e boas práticas elevadas a **prioridade máxima declarada** (nova §2.5)
> - Ferramental obrigatório (`ruff`, `mypy`, ESLint estrito, Prettier) formalizado em §2.6
> - Exemplos de código do PRD refinados com docstrings, type hints modernos e nomes consistentes
> - Gates de qualidade adicionados em §9 (NFR), §16 (critérios de aceite) e ao fim de cada fase do §18
> - TASK-00 de configuração de tooling introduzida antes de qualquer tarefa de feature
>
> **Changelog v1.2:**
> - Nova §21 (Polimento) introduzida para registrar adições e modificações pós-Fase 5
> - §21.1: autonomia do agente na seleção de visualização — remoção de exemplos e regras prescritivas do system prompt
> - §21.2: tratamento de erros de rate limit e quota do Gemini — novos códigos HTTP 429 e 503 complementares
> - §21.3: migração do ambiente de execução para Python 3.13.13

---

## 0. Como usar este documento

Este PRD é prescritivo. Todas as decisões já foram tomadas com o stakeholder e estão registradas como **fatos**, não como sugestões. Uma instância LLM consumindo este documento deve:

1. Ler integralmente antes de produzir backlog
2. Tratar §2.5, §3 e §18 como fonte de verdade para escopo e qualidade
3. Usar §10, §11, §12, §13, §14 e §15 como especificação técnica imediatamente executável
4. **Não alterar decisões arquiteturais ou padrões de código sem consulta explícita ao stakeholder**
5. Em caso de conflito entre "entregar mais rápido" e "entregar com qualidade", **qualidade vence** (ver §2.5)

---

## 1. Contexto e objetivo

### 1.1 Contexto
O projeto `RocketLab-2026-GenAI` é uma aplicação fullstack de **Gerenciamento de E-Commerce** já implementada, com:
- Backend FastAPI + SQLAlchemy + SQLite + Alembic + JWT
- Frontend React + Vite + TypeScript + Tailwind CSS
- Autenticação com perfis `admin` e `viewer`
- Suíte de testes pytest + httpx funcional

### 1.2 Objetivo da feature
Adicionar uma nova página interna **`/assistente`** onde usuários não-técnicos realizam consultas em linguagem natural sobre o banco de dados do e-commerce. O agente (PydanticAI + Gemini 2.5 Flash) traduz a pergunta para SQL, executa com guardrails de segurança, e renderiza o resultado como tabela e/ou gráfico dinamicamente.

### 1.3 Valor
- Elimina a necessidade de conhecimento SQL para obter insights do negócio
- Acelera o tempo de resposta para perguntas analíticas comuns
- Atende integralmente os requisitos da atividade Rocket Lab 2026

### 1.4 Princípios de entrega
A feature é avaliada por três eixos, em ordem de prioridade:

1. **Qualidade de código e legibilidade** (ver §2.5) — prioridade máxima; gates obrigatórios
2. **Correção funcional** — todas as perguntas-exemplo do PDF devem funcionar
3. **Polimento de UX** — anonimização, exportação, histórico, sugestões

Funcionalidade correta sem qualidade de código **não é um entregável aceitável**.

---

## 2. Stack técnica (fixa)

| Camada | Tecnologia | Observação |
|---|---|---|
| Framework de agentes | **PydanticAI** | Obrigatório (definição do stakeholder) |
| Modelo LLM | **`gemini-2.5-flash`** | Via `google-gla` provider do PydanticAI |
| Linguagem backend | Python 3.11+ | Já existente |
| Framework backend | FastAPI | Já existente |
| Parser SQL | **`sqlglot`** | Novo — para guardrails |
| ORM | SQLAlchemy 2.0 | Já existente |
| Banco de dados | SQLite (`database.db`) | Único; **sem duplicação** |
| Biblioteca de gráficos | **Recharts** | Novo — no frontend |
| Framework frontend | React + Vite + TypeScript | Já existente |
| Estilo | Tailwind CSS | Já existente; respeitar dark mode |
| Autenticação | JWT (Bearer token) | Já existente; reutilizar |
| Testes backend | pytest + httpx | Já existente; estender |
| Linter/formatter Python | **`ruff`** | Novo — obrigatório |
| Type checker Python | **`mypy`** | Novo — obrigatório |
| Linter TS | ESLint | Já existente; endurecer regras |
| Formatter TS | Prettier | Novo — obrigatório se ausente |

### 2.1 Dependências Python novas (adicionar em `backend/requirements.txt`)
```
pydantic-ai
google-genai
sqlglot
ruff
mypy
```

### 2.2 Dependências frontend novas (adicionar em `frontend/package.json`)
```
recharts
html2canvas
# devDependencies:
prettier
eslint-plugin-jsx-a11y
```

### 2.3 Variáveis de ambiente novas
| Variável | Onde | Descrição |
|---|---|---|
| `GOOGLE_API_KEY` | `backend/.env` e `backend/.env.example` | Chave da API do Gemini. Obrigatória. Sem ela o endpoint `/api/assistente/perguntar` retorna 503. |

---

## 2.5 Padrões de código e boas práticas — PRIORIDADE MÁXIMA

> **Declaração de stakeholder:** legibilidade de código e aderência a boas práticas são a prioridade número 1 desta implementação. Em qualquer conflito entre velocidade e qualidade, qualidade vence. Um módulo funcional mas ilegível deve ser refatorado antes do merge.

### 2.5.1 Princípios gerais

1. **Explícito > implícito** — type hints, nomes descritivos, estruturas tipadas em toda parte
2. **Pequeno > grande** — funções com propósito único; módulos com responsabilidade única; componentes focados
3. **Por que > o que** — comentários explicam decisões e trade-offs; o código explica o que faz
4. **Erros explícitos > silenciosos** — exceções tipadas do domínio; nunca `except:` genérico; nunca engolir erros
5. **Composição > configuração** — dependency injection via `Depends` do FastAPI, não singletons globais
6. **Imutabilidade > mutação** — Pydantic models; funções puras onde possível
7. **Nomes > comentários** — preferir renomear a comentar o óbvio

### 2.5.2 Padrões Python (backend)

#### Type hints — obrigatório
- Type hints em **todas** as funções, métodos e atributos de classe
- Sintaxe moderna Python 3.11+: `list[str]`, `dict[str, int]`, `X | None`
  - Evitar: `Optional[X]`, `List[X]`, `Dict[K, V]`
- `Any` só é permitido com `# noqa` + comentário justificando
- Usar `Literal`, `Final`, `TypeAlias`, `Protocol` quando agregam clareza

#### Docstrings — obrigatórias em módulos e API pública
Estilo Google (configurado no `ruff`). Módulos começam com docstring de 1–2 linhas descrevendo a responsabilidade. Funções privadas (`_foo`) dispensam docstring se nome + type hints forem auto-explicativos.

#### Naming

| Elemento | Convenção | Exemplo |
|---|---|---|
| Módulo / arquivo | `snake_case.py` | `sql_guardrail.py` |
| Classe | `PascalCase` | `QueryNotAllowedError` |
| Função / método / variável | `snake_case` | `validate_and_harden` |
| Constante módulo | `UPPER_SNAKE_CASE` + `Final` | `MAX_ROWS: Final[int] = 1000` |
| Privado | `_leading_underscore` | `_hash6`, `_apply_transformers` |

#### Constantes (zero magic numbers)
- Nenhum valor literal (timeout, limite, URL, string repetida) inline no código
- Extrair para constante nomeada no topo do módulo com `Final`
- Se a constante é compartilhada entre módulos, promover para `app/core/constants.py`

#### Estrutura interna de um módulo

Ordem canônica:
1. Module docstring
2. `from __future__ import annotations`
3. Imports (3 grupos: stdlib / third-party / local)
4. Constantes
5. Type aliases
6. Exceções customizadas
7. Helpers privados (`_foo`)
8. API pública

#### Funções e complexidade
- **Alvo:** ≤ 20 linhas de corpo
- **Teto:** 40 linhas de corpo; acima disso, refatorar
- **Complexidade ciclomática:** ≤ 10 (enforced via `ruff` regra `C901`)
- Máximo 3–4 parâmetros posicionais; acima disso, usar Pydantic `BaseModel` ou `dataclass`
- Funções privadas para extrair blocos `if/else` longos

#### Separação de camadas — obrigatório

```
Router (app/routers/)
  └ Apenas: definição HTTP, auth, validação de request via Pydantic, DI
  └ Delega toda lógica para serviços

Service (app/services/, app/agents/)
  └ Apenas: regras de negócio, orquestração
  └ Não conhece FastAPI (sem import de Request, HTTPException)

Repository / Query (SQLAlchemy)
  └ Apenas: acesso a dados
  └ Não conhece schemas de response

Schemas (app/schemas/)
  └ Apenas: Pydantic models de request/response
```

Violações típicas a evitar:
- SQL cru dentro de um router
- `HTTPException` sendo levantada dentro de um serviço
- Model SQLAlchemy sendo retornado diretamente como response

#### Exceções e erros

Domain exceptions ficam no módulo relevante. O tratamento HTTP é centralizado em `app/errors.py` via `register_exception_handlers(app)`, registrado em `main.py`. Regras:

- Nunca `except:` bare; nunca `except Exception:` sem re-raise ou log + handle específico
- Sempre `raise X from e` ao encadear exceções
- Mensagens de erro legíveis ao usuário final em pt-BR; detalhes técnicos via log

#### Configuração

- Tudo que vem de env var passa por `pydantic_settings.BaseSettings` em `app/config.py`
- Zero `os.getenv()` espalhado
- Settings injetado via `Depends(get_settings)` nos routers; `@lru_cache` na factory

#### Logging
- `logging` stdlib; `logger = logging.getLogger(__name__)` no topo do módulo
- **Nunca** `print()` em código de produção
- Lazy formatting em níveis ≥ INFO: `logger.info("query ran in %.2fs", elapsed)`
- Nunca logar: senhas, `GOOGLE_API_KEY`, conteúdo de `comentario`/`titulo_comentario` quando `anonimizar=True`

#### Async / sync coerência
- Rotas FastAPI → `async def`
- Chamadas a LLM (PydanticAI) → `async def`
- Lógica pura (parser, anonymizer, validação) → `def` síncrono
- Nunca `asyncio.run()` dentro de handlers

#### Import order (aplicado pelo `ruff` / isort)
Três grupos separados por linha em branco: stdlib → third-party → local.

#### Outros
- Paths: `pathlib.Path`, nunca `os.path`
- Strings: f-strings (exceto logging `INFO+`)
- Comparações: `is None` / `is not None`; `if items:` em iteráveis
- **Proibido:** mutáveis default em assinaturas (`def f(x=[])`) → usar `x: list[int] | None = None`
- `return` explícito; evitar múltiplos `return` em cadeias de `if/elif` quando prejudica leitura

#### Limites de tamanho

| Entidade | Alvo | Teto |
|---|---|---|
| Função (corpo) | 20 linhas | 40 linhas |
| Método de classe | 15 linhas | 30 linhas |
| Módulo | 200 linhas | 300 linhas |
| Classe | 150 linhas | 250 linhas |

Acima dos tetos, refatorar obrigatoriamente.

### 2.5.3 Padrões TypeScript (frontend)

#### TypeScript estrito
- `tsconfig.json`: `"strict": true`, `"noUncheckedIndexedAccess": true`, `"noImplicitAny": true`
- Zero `any` explícito; usar `unknown` + narrowing
- Return type explícito em funções exportadas

#### Naming

| Elemento | Convenção | Exemplo |
|---|---|---|
| Componente (arquivo) | `PascalCase.tsx` | `PromptInput.tsx` |
| Hook (arquivo) | `useCamelCase.ts` | `useLocalHistory.ts` |
| Utilidade (arquivo) | `camelCase.ts` | `assistenteApi.ts` |
| Tipo / type alias | `PascalCase` | `type RespostaAssistente` |
| Função / variável | `camelCase` | `perguntarAoAssistente` |
| Constante | `UPPER_SNAKE_CASE` | `const MAX_HISTORICO = 10` |
| Props type | `<Component>Props` | `type PromptInputProps` |

Preferir `type` a `interface` para consistência em todo o frontend (exceto quando extensão de interface for essencial).

#### Componentes React
- Functional components + hooks apenas (zero class components)
- `export default` para componentes; `export` nomeado para hooks/utils
- Destructuring de props na assinatura com type explícito `<Component>Props`
- **Alvo:** ≤ 150 linhas por componente; ultrapassando, extrair sub-componentes ou custom hooks
- Lógica não-visual (localStorage, chamadas axios, transformação de dados) fica em hooks/utils, nunca no componente

#### Hooks
- Prefixo `use` obrigatório
- Uma responsabilidade por hook
- Dependências de `useEffect/useMemo/useCallback` completas e corretas (ESLint regra `react-hooks/exhaustive-deps` em nível `error`)

#### Styling
- 100% Tailwind; `style={{}}` inline apenas para valores dinâmicos inexprimíveis em Tailwind
- Dark mode via `dark:` prefix consistente
- Nunca hardcoded hex em JSX

#### Acessibilidade
- HTML semântico: `<button>`, `<nav>`, `<main>`, `<section>`; não `<div onClick>`
- `aria-label` em controles sem texto visível
- `<label htmlFor>` para inputs
- Foco visível (Tailwind `focus:ring-*`)
- Contraste WCAG AA

#### Tipagem de API
- Tipos em `src/types/assistente.ts` espelhando **exatamente** os schemas Pydantic do backend
- Zero duck-typing; `axios.post<RespostaAssistente>(...)` tipado
- Funções exportadas com return type explícito

### 2.5.4 Padrões de testes

- **AAA pattern** explicitado com comentários quando ajuda leitura
- Nomes: `test_<subject>_<condition>_<expected>`
- Um conceito por teste (múltiplos asserts OK quando testam o mesmo comportamento)
- `pytest.fixture` sobre setup/teardown
- `pytest.mark.parametrize` para famílias de casos similares
- Zero interdependência entre testes
- Mocks apenas em fronteiras externas (LLM, rede); lógica pura testada sem mocks

---

## 2.6 Ferramental de qualidade — obrigatório

### 2.6.1 Backend — `backend/pyproject.toml`

```toml
[tool.ruff]
line-length = 100
target-version = "py311"
extend-exclude = ["alembic/versions"]

[tool.ruff.lint]
select = [
    "E", "F", "W",   # pycodestyle + pyflakes
    "I",             # isort
    "UP",            # pyupgrade
    "B",             # flake8-bugbear
    "N",             # pep8-naming
    "D",             # pydocstyle
    "C90",           # mccabe complexity
    "RUF",           # ruff-specific
]
ignore = ["D203", "D212"]

[tool.ruff.lint.pydocstyle]
convention = "google"

[tool.ruff.lint.mccabe]
max-complexity = 10

[tool.ruff.lint.per-file-ignores]
"tests/*" = ["D"]
"alembic/*" = ["D"]

[tool.ruff.format]
quote-style = "double"

[tool.mypy]
python_version = "3.11"
strict = true
warn_unreachable = true
plugins = ["pydantic.mypy"]

[[tool.mypy.overrides]]
module = ["sqlglot.*", "google.genai.*", "pydantic_ai.*"]
ignore_missing_imports = true
```

**Comandos padronizados (documentar no README):**
```bash
cd backend
ruff format .
ruff check . --fix
mypy app/
pytest tests/ -v
pytest --cov=app --cov-report=term-missing
```

### 2.6.2 Frontend

ESLint endurecido:
- `@typescript-eslint/no-explicit-any: "error"`
- `@typescript-eslint/explicit-module-boundary-types: "warn"`
- `react-hooks/exhaustive-deps: "error"`
- `jsx-a11y/*` (preset recomendado)

`.prettierrc`:
```json
{
  "singleQuote": true,
  "trailingComma": "all",
  "printWidth": 100,
  "semi": true,
  "arrowParens": "always"
}
```

Scripts em `package.json`:
```json
{
  "scripts": {
    "lint": "eslint src --max-warnings 0",
    "format": "prettier --write src",
    "format:check": "prettier --check src",
    "type-check": "tsc --noEmit"
  }
}
```

### 2.6.3 Gates de qualidade (obrigatórios antes de "pronto")

- [ ] `ruff format --check .` sem diff
- [ ] `ruff check .` 0 issues
- [ ] `mypy app/` 100% em strict mode
- [ ] `pytest tests/ -v` 100%
- [ ] Cobertura ≥ 80% nos módulos novos (§15.2)
- [ ] `npm run lint` 0 warnings
- [ ] `npm run type-check` 0 errors
- [ ] `npm run format:check` sem diff

---

## 3. Decisões consolidadas

| # | Decisão | Valor | Justificativa |
|---|---|---|---|
| D0 | **Prioridade nº 1** | **Legibilidade e boas práticas** | Declaração explícita do stakeholder |
| D1 | Banco de dados | Base única + conexão read-only | Simplicidade, zero sincronização |
| D2 | Biblioteca de gráficos | Recharts | Integração nativa com React/Tailwind |
| D3 | Rota da dashboard | `/assistente` | Escolhida pelo stakeholder |
| D4 | Controle de acesso | Página visível para admin e viewer; envio de prompt apenas admin | UX amigável + segurança |
| D5 | Memória de conversa | Stateless | Simplicidade, previsibilidade |
| D6a | Guardrail de escrita | SELECT-only (`sqlglot` + SQLite `mode=ro`) | Defesa em camadas |
| D6b | Guardrail de tabela | Blacklist de `usuarios` | Protege `hashed_password` |
| D6c | Guardrail de volume | `LIMIT 1000` forçado se ausente | Protege UI e API |
| D6d | Guardrail de tema | Rejeição de prompts off-topic | Mantém foco em dados |
| D7 | Mostrar SQL gerado | Sim, colapsável na UI | Transparência e debug |
| D8 | Perguntas sugeridas | Sim, usando exemplos do PDF | Onboarding |
| D9 | Exportação | CSV (tabelas) + PNG (gráficos) | Reuso em outras ferramentas |
| D10 | Histórico | `localStorage` (sem tabela nova) | MVP simples, privacidade por usuário |
| D11 | Anonimização | Runtime no backend + toggle 🔒 + hash SHA-1 determinístico | LGPD sem duplicar base |
| D12 | Arquitetura backend | Novo router no backend atual | Deploy unificado |
| D13 | Modos de execução | **Docker e sem Docker** | Requisito explícito |
| D14 | Contrato da resposta | Sempre tabela + gráfico opcional | Ver §7.2 |
| D15 | Tom do agente | Smart two-pass condicional (3–100 linhas + coluna numérica) | Insight com custo aceitável |
| D16 | Tratamento de erro | Retry automático (máx 2) + fallback amigável | Padrão de Text-to-SQL |
| D17 | Idioma | pt-BR | Consistência com app |
| D18 | Testes | Backend obrigatório (semi-TDD); frontend e LLM opcionais | Definição do stakeholder |
| D19 | **Ferramental backend** | `ruff` + `mypy` (strict) — obrigatórios | Prioridade de qualidade |
| D20 | **Ferramental frontend** | ESLint endurecido + Prettier — obrigatórios | Prioridade de qualidade |

---

## 4. Schema do banco de dados (referência para o agente)

> **IMPORTANTE:** Este schema é injetado no system prompt do agente. Os nomes aqui são a fonte de verdade — não existem tabelas `dim_*` ou `fat_*`.

### Tabelas

**`consumidores`** — clientes finais
- `id_consumidor` (String 32, PK)
- `prefixo_cep` (String 10)
- `nome_consumidor` (String 255) 🔒 PII
- `cidade` (String 100)
- `estado` (String 2)

**`vendedores`** — vendedores cadastrados
- `id_vendedor` (String 32, PK)
- `nome_vendedor` (String 255) 🔒 PII
- `prefixo_cep` (String 10)
- `cidade` (String 100)
- `estado` (String 2)

**`produtos`** — catálogo (contém colunas desnormalizadas/agregadas)
- `id_produto` (String 32, PK)
- `nome_produto` (String 255)
- `categoria_produto` (String 100)
- `peso_produto_gramas` (Float, nullable)
- `comprimento_centimetros` (Float, nullable)
- `altura_centimetros` (Float, nullable)
- `largura_centimetros` (Float, nullable)
- `total_vendas` (Integer, default 0, not null) — agregado
- `preco_medio` (Float, nullable) — agregado
- `total_avaliacoes` (Integer, default 0, not null) — agregado
- `avaliacao_media` (Float, nullable) — agregado

**`pedidos`** — cabeçalho dos pedidos
- `id_pedido` (String 32, PK)
- `id_consumidor` (String 32, FK → `consumidores.id_consumidor`, not null)
- `status` (String 50)
- `pedido_compra_timestamp` (DateTime, nullable)
- `pedido_entregue_timestamp` (DateTime, nullable)
- `data_estimada_entrega` (Date, nullable)
- `tempo_entrega_dias` (Float, nullable)
- `tempo_entrega_estimado_dias` (Float, nullable)
- `diferenca_entrega_dias` (Float, nullable) — positivo = atraso
- `entrega_no_prazo` (String 10, nullable) — **não é boolean**; valores a confirmar

**`itens_pedidos`** — itens de cada pedido
- PK composta: `(id_pedido, id_item)`
- `id_pedido` (String 32, FK → `pedidos.id_pedido`, not null)
- `id_item` (Integer, not null)
- `id_produto` (String 32, FK → `produtos.id_produto`, not null, indexado)
- `id_vendedor` (String 32, FK → `vendedores.id_vendedor`, not null)
- `preco_BRL` (Float)
- `preco_frete` (Float)

**`avaliacoes_pedidos`** — reviews de pedidos
- `id_avaliacao` (String 32, PK)
- `id_pedido` (String 32, FK → `pedidos.id_pedido`, not null, indexado)
- `avaliacao` (Integer) — escala 1–5
- `titulo_comentario` (String 255, nullable) 🔒 PII potencial
- `comentario` (String 1000, nullable) 🔒 PII potencial
- `data_comentario` (DateTime, nullable)
- `data_resposta` (DateTime, nullable)
- `resposta_admin` (Text, nullable)
- `autor_resposta` (String 255, nullable)

**`usuarios`** — ⛔ **BLOQUEADA** para o agente (contém `hashed_password`)
- `id_usuario` (String 32, PK)
- `username` (String 255, único, indexado)
- `hashed_password` (String 255)
- `is_admin` (Boolean, default False)

### 4.1 Observações de modelagem

- **Receita total de um pedido** é derivada: `SUM(preco_BRL + preco_frete)` sobre `itens_pedidos`
- **Receita por categoria:** join `itens_pedidos → produtos`, `GROUP BY categoria_produto`
- **Receita por estado:** join `itens_pedidos → pedidos → consumidores`, `GROUP BY estado`
- Colunas agregadas em `produtos` são atalhos; **o agente deve preferir joins a partir das tabelas de fato**
- `pedidos.entrega_no_prazo` é `String(10)` — NÃO usar `= TRUE`; usar `= 'sim'` / `= 'nao'` (valores a confirmar no banco durante implementação)

---

## 5. Personas e permissões

| Persona | Acesso a `/assistente` | Pode enviar prompt | Pode usar toggle 🔒 | Pode exportar |
|---|---|---|---|---|
| **Admin** | ✅ | ✅ | ✅ | ✅ |
| **Viewer** | ✅ (visualiza UI) | ❌ (input desabilitado) | N/A | N/A |
| **Não autenticado** | ❌ (redirect login) | N/A | N/A | N/A |

### 5.1 UX para viewer
- Input `disabled` com placeholder `"Funcionalidade restrita a administradores"`
- Tooltip: `"Contate seu gestor para obter acesso de administrador"`
- Sample questions renderizadas mas desabilitadas
- Sidebar de histórico visível, mas vazia

---

## 6. User stories

### US-01 — Consulta simples de admin
**Como** administrador, **quero** digitar `"Top 10 produtos mais vendidos"` e apertar Enviar, **para** ver tabela e gráfico de barras em menos de 5 segundos.
**Critérios:** tabela com 10 linhas; gráfico de barras com os mesmos dados; SQL visível em seção colapsável; resposta ≤ 5s.

### US-02 — Resultado de 1 valor
**Como** admin, **quero** `"Qual a média de avaliação geral dos pedidos?"`, **para** ver 1 linha sem gráfico.
**Critérios:** apenas tabela; gráfico omitido (resultado unitário).

### US-03 — Apenas gráfico
**Como** admin, **quero** `"Me dá apenas o gráfico de pedidos por status"`, **para** ver só o gráfico.
**Critérios:** agente detecta exclusão; resposta contém apenas gráfico.

### US-04 — Anonimização
**Como** admin preparando apresentação, **quero** ativar toggle 🔒, **para** mascarar nomes na tela.
**Critérios:** toggle visível; `nome_consumidor` vira `Consumidor_abc123`; hash determinístico.

### US-05 — Prompt malicioso
**Como** admin digitando `"DROP TABLE produtos"`, **quero** mensagem de bloqueio clara.
**Critérios:** HTTP 400 com `erro: "query_rejeitada"`; UI mostra `"Apenas consultas de leitura são permitidas."`

### US-06 — Viewer visualiza a feature
**Como** viewer, **quero** acessar `/assistente`, **para** saber que existe.
**Critérios:** página renderiza; input desabilitado; POST direto → 403.

### US-07 — Reusar histórico
**Como** admin, **quero** ver últimas 10 perguntas na lateral.
**Critérios:** ordem reversa cronológica; click preenche input; botão "Limpar" zera.

### US-08 — Exportar
**Como** admin, **quero** baixar tabela como CSV e gráfico como PNG.
**Critérios:** botões "⬇ CSV" e "⬇ PNG" funcionais.

### US-09 — Off-topic
**Como** admin digitando `"me escreve um poema"`, **quero** recusa educada.
**Critérios:** agente explica escopo da ferramenta; não gera SQL.

---

## 7. Fluxos funcionais

### 7.1 Fluxo principal (success path)

```
Admin digita pergunta → POST /api/assistente/perguntar
  ↓
Router valida auth (admin obrigatório) + schema Pydantic
  ↓
Service orquestra:
  SQL Agent (pass 1) → SqlGenerationResult
  ↓
  Guardrail (validate_and_harden) → SQL hardened
  ↓
  Execução na engine read-only (timeout 10s)
  ↓
  Anonymizer (se flag ativo) → rows mascaradas
  ↓
  Condição two-pass (3 ≤ linhas ≤ 100 + coluna numérica):
    ├─ SIM → Insight Agent (pass 2) → explicação analítica
    └─ NÃO → explicação seca do pass 1
  ↓
  Compose visualizações (tabela + gráfico opcional)
  ↓
Router serializa → RespostaAssistente
```

### 7.2 Regras de composição de `visualizacoes`

| Cenário (detectado na pergunta) | Tabela | Gráfico |
|---|---|---|
| Neutro (`"Top 10 produtos"`) | ✅ | ➕ se útil (§7.3) |
| Pede gráfico (`"faz um gráfico de..."`) | ✅ | ✅ |
| Pede tabela (`"me dá a tabela de..."`) | ✅ | ❌ |
| Exclui tabela (`"apenas o gráfico"`, `"sem tabela"`) | ❌ | ✅ |
| Resultado unitário | ✅ (1 linha) | ❌ |

### 7.3 Heurística de seleção de gráfico

| Formato dos dados | Gráfico sugerido |
|---|---|
| 1 dim. categórica (N ≤ 20) + 1 medida | **bar** |
| 1 dim. categórica (N > 20) + 1 medida | tabela apenas |
| 1 dim. temporal + 1 medida | **line** |
| 1 dim. categórica (N ≤ 6) como % de 100 | **pie** |
| 1 dim. temporal + 2+ medidas | **area** |
| 2 dim. numéricas (correlação) | **scatter** |
| 1 linha / 1 valor | nenhum |

### 7.4 Fluxo de erro (retry + fallback)

```
Tentativa 1: Agent gera SQL
  ↓
Execução falha (syntax / guardrail / DB error)
  ↓
Tentativa 2: Agent recebe (erro + SQL anterior) e retenta
  ↓
Tentativa 3: idem
  ↓
Todas falharam?
  ├─ SIM → HTTP 200 com erro_amigavel:
  │        "Não consegui responder sua pergunta. Tente reformular,
  │         por exemplo especificando períodos, estados ou categorias."
  └─ NÃO → fluxo principal
```

**Status HTTP:** fallback após retries é **200 com campo `erro_amigavel`**. Status 4xx/5xx reservados para falhas técnicas (auth, validação, guardrail bloqueando antes de retry).

### 7.5 Fluxo de anonimização

```
Toggle 🔒 ativo → flag anonimizar=true no request
  ↓
Query executada com dados reais
  ↓
Antes da serialização, anonymize_rows() varre resultados
  ↓
Para cada coluna em PII_TRANSFORMERS: aplica transformer determinístico
  ↓
Hash = SHA-1(valor) truncado a 6 chars
```

### 7.6 Fluxo de histórico

```
Após resposta bem-sucedida:
  localStorage["assistente:historico"].push({pergunta, timestamp})
  Trunca a 10 (FIFO)
  ↓
Mount da página:
  Lê localStorage e renderiza sidebar
  ↓
Click em item: preenche input (não reexecuta)
  ↓
Botão "Limpar": localStorage.removeItem(...)
```

---

## 8. Requisitos funcionais

### 8.1 Frontend — página `/assistente`

**Layout (desktop):**
```
┌──────────────────────────────────────────────────────────┐
│ Navbar (link "Assistente")                                │
├─────────┬────────────────────────────────────────────────┤
│ Histór. │ [Toggle 🔒 Modo anônimo]                        │
│ (10)    │ ┌────────────────────────────────────────────┐ │
│ - P1    │ │ Digite sua pergunta...       [Enviar →]    │ │
│ - P2    │ └────────────────────────────────────────────┘ │
│ ...     │ Sugestões: [Top 10 produtos] [Pedidos/status] │
│ [Limpar]│ ─── Resultado ───                              │
│         │ [▸ Ver SQL]                                    │
│         │ <Explicação>                                   │
│         │ <Tabela>                 [⬇ CSV]               │
│         │ <Gráfico>                [⬇ PNG]               │
└─────────┴────────────────────────────────────────────────┘
```

**Mobile:** sidebar colapsável (hamburger); tabelas com scroll horizontal; `ResponsiveContainer` do Recharts.

**Componentes (em `frontend/src/components/assistente/`):**

| Componente | Responsabilidade | Alvo LoC |
|---|---|---|
| `AssistentePage.tsx` | Container principal (em `pages/`) | ≤ 150 |
| `PromptInput.tsx` | Input + envio + validação de perfil | ≤ 80 |
| `SampleQuestions.tsx` | Cards de perguntas sugeridas | ≤ 60 |
| `HistorySidebar.tsx` | Lista localStorage | ≤ 100 |
| `AnonymizeToggle.tsx` | Switch 🔒 | ≤ 40 |
| `ResultRenderer.tsx` | Orquestra `visualizacoes[]` | ≤ 80 |
| `SQLViewer.tsx` | Colapsável "Ver SQL" | ≤ 50 |
| `DynamicTable.tsx` | Tabela + export CSV | ≤ 120 |
| `DynamicChart.tsx` | Router para subtipos + export PNG | ≤ 80 |
| `charts/Chart{Bar,Line,Pie,Area,Scatter}.tsx` | Wrappers Recharts | ≤ 80 cada |
| `ErrorMessage.tsx` | Render de `erro_amigavel` | ≤ 40 |

**Hooks (`frontend/src/hooks/`):** `useLocalHistory.ts`
**API (`frontend/src/api/`):** `assistenteApi.ts`

### 8.2 Backend — router `/api/assistente`

**Novos módulos (em `backend/app/`):**

| Módulo | Responsabilidade |
|---|---|
| `routers/assistente.py` | HTTP, auth, DI |
| `services/assistente_service.py` | **Orquestração principal** (agent → guardrail → DB → anonymize → compose) |
| `agents/sql_agent.py` | PydanticAI pass 1 |
| `agents/insight_agent.py` | PydanticAI pass 2 |
| `agents/schema_context.py` | Constante com schema formatado |
| `services/sql_guardrail.py` | Validação `sqlglot` |
| `services/anonymizer.py` | PII masking |
| `services/readonly_db.py` | Engine read-only |
| `services/retry.py` | Loop de retry |
| `schemas/assistente.py` | Pydantic request/response |
| `errors.py` | Handlers centralizados de exceções do domínio |

**Endpoints:**

| Método | Rota | Perfil |
|---|---|---|
| `POST` | `/api/assistente/perguntar` | Admin |
| `GET` | `/api/assistente/saude` | Público |

### 8.3 Agentes (PydanticAI)

**SQL Agent (`sql_agent`)** — sempre executado
- Input: pergunta + schema + (histórico de erros se retry)
- Output: `SqlGenerationResult` com `sql`, `explicacao_seca`, `sugestao_grafico`, `grafico_config`, `forcar_tabela`, `eh_off_topic`, `mensagem_off_topic`

**Insight Agent (`insight_agent`)** — condicional
- Input: pergunta + dados (top 100 linhas) + explicação seca
- Output: `InsightResult` com `explicacao_analitica` (2–4 frases)
- Condição: `3 ≤ rows ≤ 100` E ≥ 1 coluna numérica
- Prompt tem instrução rígida anti-alucinação (§12.2)

---

## 9. Requisitos não-funcionais

### 9.1 Performance
| Requisito | Target |
|---|---|
| Latência p50 (single-pass) | ≤ 3s |
| Latência p95 (two-pass) | ≤ 6s |
| Timeout de query SQL | 10s |

### 9.2 Funcional
| Requisito | Target |
|---|---|
| Taxa de sucesso (10 perguntas do PDF) | ≥ 90% |
| Responsividade | ≥ 360px |
| Dark mode | 100% suportado |
| Idioma | pt-BR |
| Execução | Docker **e** sem Docker |

### 9.3 Qualidade de código (obrigatórios)
| Requisito | Target |
|---|---|
| `ruff check .` | 0 issues |
| `ruff format --check .` | sem diff |
| `mypy app/` | 0 errors (strict) |
| Complexidade ciclomática por função | ≤ 10 |
| Cobertura de testes nos módulos novos | ≥ 80% |
| Docstrings em API pública do backend | ≥ 90% |
| `npm run lint` | 0 warnings |
| `npm run type-check` | 0 errors |
| `npm run format:check` | sem diff |
| Tamanho máximo de módulo Python | 300 linhas |
| Tamanho máximo de componente React | 150 linhas |


---

## 10. Guardrails (especificação detalhada)

### 10.1 Camada 1 — Engine SQLite read-only

Módulo `backend/app/services/readonly_db.py`:

```python
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
```

### 10.2 Camada 2 — Parser SQL (`sqlglot`)

Módulo `backend/app/services/sql_guardrail.py`:

```python
"""SQL query validation against security guardrails.

All agent-generated queries pass through ``validate_and_harden`` before
execution. The function raises ``QueryNotAllowedError`` on any violation
and otherwise returns a hardened SQL string with a safe ``LIMIT``.
"""
from __future__ import annotations

from typing import Final

import sqlglot
from sqlglot import exp

MAX_ROWS: Final[int] = 1000
FORBIDDEN_TABLES: Final[frozenset[str]] = frozenset({"usuarios"})


class QueryNotAllowedError(ValueError):
    """Raised when a SQL query violates security guardrails."""


def validate_and_harden(sql: str) -> str:
    """Validate SQL and return a hardened version with safe ``LIMIT``.

    Checks applied in order:
      1. SQL is parseable as SQLite dialect.
      2. Exactly one statement (no multi-statement injection).
      3. The statement is a ``SELECT`` (no DDL/DML).
      4. No forbidden table is referenced.
      5. ``LIMIT`` is injected or capped to ``MAX_ROWS``.

    Args:
        sql: Raw SQL produced by the agent.

    Returns:
        The SQL with a safe ``LIMIT`` clause.

    Raises:
        QueryNotAllowedError: If any guardrail is violated.
    """
    tree = _parse_single_statement(sql)
    _ensure_select(tree)
    _ensure_no_forbidden_tables(tree)
    return _enforce_limit(tree).sql(dialect="sqlite")


def _parse_single_statement(sql: str) -> exp.Expression:
    try:
        parsed = sqlglot.parse(sql, dialect="sqlite")
    except sqlglot.errors.ParseError as exc:
        raise QueryNotAllowedError(f"SQL malformado: {exc}") from exc

    if len(parsed) != 1 or parsed[0] is None:
        raise QueryNotAllowedError("Apenas uma consulta por vez é permitida.")

    return parsed[0]


def _ensure_select(tree: exp.Expression) -> None:
    if not isinstance(tree, exp.Select):
        raise QueryNotAllowedError("Apenas consultas SELECT são permitidas.")


def _ensure_no_forbidden_tables(tree: exp.Expression) -> None:
    for table in tree.find_all(exp.Table):
        if table.name.lower() in FORBIDDEN_TABLES:
            raise QueryNotAllowedError(
                f"Consultas à tabela '{table.name}' não são permitidas."
            )


def _enforce_limit(tree: exp.Select) -> exp.Select:
    existing = tree.args.get("limit")
    if existing is None:
        return tree.limit(MAX_ROWS)

    try:
        current = int(existing.expression.name)
    except (ValueError, AttributeError):
        return tree.limit(MAX_ROWS)

    return tree.limit(MAX_ROWS) if current > MAX_ROWS else tree
```

Este exemplo já exemplifica os padrões de §2.5: module docstring, `Final`, `frozenset`, funções privadas curtas, type hints modernos, Google-style docstring, `raise ... from exc`.

### 10.3 Camada 3 — System prompt
Instruções explícitas para o agente (ver §12.1): gerar apenas SELECT, nunca referenciar `usuarios`, sempre incluir `LIMIT`, recusar off-topic.

### 10.4 Ordem de aplicação

1. Agente gera SQL
2. `validate_and_harden()` valida ou levanta
3. Query executada na engine read-only
4. Se falhou nas camadas 1 ou 2 → dispara retry com contexto

---

## 11. Contrato da API

### 11.1 `POST /api/assistente/perguntar`

**Auth:** Bearer JWT; `is_admin=True`.

**Request:**
```json
{
  "pergunta": "Top 10 produtos mais vendidos",
  "anonimizar": false
}
```

**Response 200 (sucesso):**
```json
{
  "pergunta": "Top 10 produtos mais vendidos",
  "sql_gerado": "SELECT nome_produto, total_vendas FROM produtos ORDER BY total_vendas DESC LIMIT 10",
  "explicacao": "Listei os 10 produtos com maior volume de vendas...",
  "visualizacoes": [
    {
      "tipo": "tabela",
      "titulo": "Top 10 produtos mais vendidos",
      "colunas": ["nome_produto", "total_vendas"],
      "linhas": [["Produto A", 1234], ["Produto B", 987]]
    },
    {
      "tipo": "grafico",
      "subtipo": "bar",
      "titulo": "Top 10 produtos mais vendidos",
      "eixo_x": "nome_produto",
      "eixo_y": "total_vendas",
      "dados": [
        {"nome_produto": "Produto A", "total_vendas": 1234},
        {"nome_produto": "Produto B", "total_vendas": 987}
      ]
    }
  ],
  "tentativas": 1,
  "metadados": {
    "anonimizado": false,
    "linhas_retornadas": 10,
    "usou_insight": true
  }
}
```

**Response 200 (fallback amigável):**
```json
{
  "pergunta": "me escreve um poema",
  "sql_gerado": null,
  "explicacao": null,
  "visualizacoes": [],
  "tentativas": 1,
  "erro_amigavel": "Esta ferramenta responde apenas perguntas sobre os dados do e-commerce. Exemplos: 'Top 10 produtos mais vendidos', 'Pedidos por status'.",
  "metadados": {"motivo": "off_topic", "anonimizado": false, "linhas_retornadas": 0, "usou_insight": false}
}
```

**Response 400 — guardrail rejeitou:** `{"detail": {"erro": "query_rejeitada", "motivo": "..."}}`
**Response 401:** `{"detail": "Not authenticated"}`
**Response 403:** `{"detail": "Apenas administradores podem utilizar o assistente."}`
**Response 422:** validação Pydantic
**Response 503:** `{"detail": "Serviço de IA não configurado. Contate o administrador."}`

### 11.2 Schemas Pydantic (`backend/app/schemas/assistente.py`)

```python
"""Request and response schemas for the /api/assistente endpoint."""
from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class PerguntaRequest(BaseModel):
    """Payload for the /perguntar endpoint."""

    model_config = ConfigDict(extra="forbid")

    pergunta: str = Field(min_length=3, max_length=500)
    anonimizar: bool = False


class TabelaVisualizacao(BaseModel):
    """Tabular visualization block."""

    tipo: Literal["tabela"] = "tabela"
    titulo: str
    colunas: list[str]
    linhas: list[list[Any]]


class GraficoVisualizacao(BaseModel):
    """Chart visualization block."""

    tipo: Literal["grafico"] = "grafico"
    subtipo: Literal["bar", "line", "pie", "area", "scatter"]
    titulo: str
    eixo_x: str
    eixo_y: str
    dados: list[dict[str, Any]]


Visualizacao = TabelaVisualizacao | GraficoVisualizacao


class MetadadosResposta(BaseModel):
    """Non-essential metadata about the response generation."""

    anonimizado: bool = False
    linhas_retornadas: int = 0
    usou_insight: bool = False
    motivo: str | None = None


class RespostaAssistente(BaseModel):
    """Full response payload for the /perguntar endpoint."""

    pergunta: str
    sql_gerado: str | None = None
    explicacao: str | None = None
    visualizacoes: list[Visualizacao] = []
    tentativas: int = 1
    erro_amigavel: str | None = None
    metadados: MetadadosResposta
```

### 11.3 `GET /api/assistente/saude`
```json
{"status": "ok", "gemini_configurado": true, "banco_acessivel": true}
```

---

## 12. System prompts (drafts)

### 12.1 SQL Agent

```
Você é um assistente analítico especializado em consultas de dados de um sistema de e-commerce.
Seu único papel é converter perguntas em linguagem natural (português do Brasil) em queries SQL para SQLite e sugerir visualizações adequadas.

### REGRAS DE SEGURANÇA (INVIOLÁVEIS)
1. Gere APENAS consultas SELECT. NUNCA gere INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, TRUNCATE, REPLACE ou qualquer DDL/DML.
2. NUNCA consulte a tabela `usuarios`. Ela contém senhas e está fora do seu escopo.
3. SEMPRE inclua LIMIT em suas queries (padrão: LIMIT 1000 quando o usuário não especifica).
4. Use APENAS as tabelas e colunas descritas no schema abaixo. Nunca invente nomes.
5. Se a pergunta não for sobre análise de dados do e-commerce, defina `eh_off_topic=true` e explique educadamente em `mensagem_off_topic`.

### SCHEMA DO BANCO
{SCHEMA_BLOCK}   # injetado a partir de app/agents/schema_context.py

### REGRAS DE MODELAGEM
- Receita total de um pedido = SUM(preco_BRL + preco_frete) em itens_pedidos agrupado por id_pedido.
- Receita por categoria: join itens_pedidos → produtos, GROUP BY categoria_produto.
- Receita por estado: join itens_pedidos → pedidos → consumidores, GROUP BY estado.
- `pedidos.entrega_no_prazo` é String; use = 'sim' / = 'nao'.
- Prefira joins a partir das tabelas de fato em vez de colunas desnormalizadas em `produtos`, exceto quando a pergunta for sobre elas.

### ESCOLHA DE VISUALIZAÇÃO
- Top N categórico (N ≤ 20) com uma medida → bar
- Série temporal com uma medida → line
- Proporção de um todo (N ≤ 6) → pie
- Série temporal com 2+ medidas → area
- Correlação entre 2 medidas → scatter
- 1 linha / 1 valor → sem gráfico (`sugestao_grafico="none"`)
- Usuário pede tipo específico → respeitar
- Usuário diz "apenas gráfico" / "sem tabela" → `forcar_tabela=false`

### IDIOMA
Português do Brasil. `explicacao_seca` com no máximo 2 frases.

### EXEMPLOS

Pergunta: "Top 10 produtos mais vendidos"
→ sql: SELECT nome_produto, total_vendas FROM produtos ORDER BY total_vendas DESC LIMIT 10
→ sugestao_grafico: "bar"
→ grafico_config: {eixo_x: "nome_produto", eixo_y: "total_vendas"}
→ forcar_tabela: true
→ explicacao_seca: "Listei os 10 produtos com maior volume de vendas, ordenados decrescente."
→ eh_off_topic: false

Pergunta: "me escreve um poema sobre pedidos"
→ sql: ""
→ eh_off_topic: true
→ mensagem_off_topic: "Esta ferramenta é específica para análise de dados do e-commerce."
```

### 12.2 Insight Agent

```
Você analisa resultados tabulares de consultas SQL e produz um comentário analítico curto em pt-BR.

### REGRAS RÍGIDAS ANTI-ALUCINAÇÃO
1. Use APENAS os números presentes nos dados fornecidos. Nunca invente valores.
2. NÃO extrapole para o futuro. NÃO invente tendências temporais.
3. NÃO mencione causas ou explicações de negócio — você não tem esse contexto.
4. NÃO compare com benchmarks externos.
5. Máximo 2-4 frases.

### O QUE FAZER
- Destacar maior e menor da coluna numérica principal.
- Calcular concentração quando aplicável ("top 3 representam X% do total listado").
- Apontar categoria mais frequente se houver dimensão categórica pequena.

### EXEMPLO
Dados: [{produto: "A", vendas: 100}, {produto: "B", vendas: 50}, {produto: "C", vendas: 10}]
Output: "O produto A lidera com 100 vendas, mais que o dobro do segundo colocado (B, 50). Juntos, A e B concentram 94% das vendas listadas."
```

### 12.3 Retry context

Injetado na próxima tentativa após falha:
```
Sua tentativa anterior falhou com o seguinte erro:
SQL gerado: {sql_anterior}
Erro: {mensagem_erro}

Corrija o problema e gere uma nova query. Lembre-se das regras de segurança: apenas SELECT, nunca `usuarios`, sempre LIMIT.
```

---

## 13. Anonimização — especificação

### 13.1 Módulo `backend/app/services/anonymizer.py`

```python
"""Deterministic PII masking for query results.

When the client sets ``anonimizar=true``, rows returned by the agent
are passed through ``anonymize_rows`` before serialization. Masking is
column-based (by column name), deterministic (SHA-1 truncated), and
null-safe.
"""
from __future__ import annotations

import hashlib
import re
from collections.abc import Callable
from typing import Any, Final

_HASH_LENGTH: Final[int] = 6
_COMMENT_MAX_LENGTH: Final[int] = 40
_NUMBER_PATTERN: Final[re.Pattern[str]] = re.compile(r"\d{3,}")


def _hash6(value: str) -> str:
    """Return the first 6 hex chars of SHA-1(value)."""
    return hashlib.sha1(value.encode("utf-8")).hexdigest()[:_HASH_LENGTH]


def _mask_cep(value: str | None) -> str | None:
    if not value:
        return value
    return f"{value[:2]}***"


def _redact_comment(value: str | None) -> str | None:
    if not value:
        return value
    trimmed = value[:_COMMENT_MAX_LENGTH]
    if len(value) > _COMMENT_MAX_LENGTH:
        trimmed = f"{trimmed}…"
    return _NUMBER_PATTERN.sub("***", trimmed)


def _hash_name(prefix: str) -> Callable[[str | None], str | None]:
    def _apply(value: str | None) -> str | None:
        if not value:
            return value
        return f"{prefix}_{_hash6(value)}"
    return _apply


PII_TRANSFORMERS: Final[dict[str, Callable[[Any], Any]]] = {
    "nome_consumidor": _hash_name("Consumidor"),
    "nome_vendedor": _hash_name("Vendedor"),
    "autor_resposta": _hash_name("Usuario"),
    "prefixo_cep": _mask_cep,
    "comentario": _redact_comment,
    "titulo_comentario": _redact_comment,
}


def anonymize_rows(
    columns: list[str],
    rows: list[list[Any]],
    enabled: bool,
) -> list[list[Any]]:
    """Apply deterministic PII masking to rows based on column names.

    Args:
        columns: Ordered list of column names.
        rows: List of rows where each row matches ``columns`` in order.
        enabled: If ``False``, returns ``rows`` unchanged.

    Returns:
        New list of rows with PII columns masked.
    """
    if not enabled:
        return rows

    transformers = [PII_TRANSFORMERS.get(col) for col in columns]

    return [
        [transformer(value) if transformer else value
         for transformer, value in zip(transformers, row, strict=True)]
        for row in rows
    ]
```

### 13.2 Propriedades garantidas

- **Determinístico:** mesmo nome → mesmo hash (permite agrupamento visual)
- **Unidirecional:** hash não-reversível
- **Colunas não-PII preservadas**
- **Null-safe**
- **`strict=True`** no `zip` pega desalinhamento entre colunas e linhas

### 13.3 Gráficos
Os `dados` do gráfico também passam pela anonimização (mesmas colunas).


---

## 14. Estrutura de arquivos

### 14.1 Novos arquivos — backend

```
backend/
├── pyproject.toml                   # NOVO — ruff/mypy config
├── app/
│   ├── errors.py                    # NOVO — handlers de exceção
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── schema_context.py
│   │   ├── sql_agent.py
│   │   └── insight_agent.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── assistente_service.py    # NOVO — orquestrador principal
│   │   ├── readonly_db.py
│   │   ├── sql_guardrail.py
│   │   ├── anonymizer.py
│   │   └── retry.py
│   ├── routers/
│   │   └── assistente.py
│   └── schemas/
│       └── assistente.py
└── tests/
    ├── test_sql_guardrail.py
    ├── test_anonymizer.py
    ├── test_readonly_db.py
    ├── test_retry.py
    └── test_assistente_endpoint.py
```

### 14.2 Novos arquivos — frontend

```
frontend/
├── .prettierrc                       # NOVO
├── src/
│   ├── api/
│   │   └── assistenteApi.ts
│   ├── types/
│   │   └── assistente.ts
│   ├── pages/
│   │   └── AssistentePage.tsx
│   ├── hooks/
│   │   └── useLocalHistory.ts
│   └── components/
│       └── assistente/
│           ├── PromptInput.tsx
│           ├── SampleQuestions.tsx
│           ├── HistorySidebar.tsx
│           ├── AnonymizeToggle.tsx
│           ├── ResultRenderer.tsx
│           ├── SQLViewer.tsx
│           ├── DynamicTable.tsx
│           ├── DynamicChart.tsx
│           ├── ErrorMessage.tsx
│           └── charts/
│               ├── ChartBar.tsx
│               ├── ChartLine.tsx
│               ├── ChartPie.tsx
│               ├── ChartArea.tsx
│               └── ChartScatter.tsx
```

### 14.3 Arquivos modificados

| Arquivo | Mudança |
|---|---|
| `backend/requirements.txt` | `pydantic-ai`, `google-genai`, `sqlglot`, `ruff`, `mypy` |
| `backend/app/main.py` | Registrar `assistente.router` + `register_exception_handlers(app)` |
| `backend/app/config.py` | Adicionar `google_api_key` em `Settings` |
| `backend/.env.example` | Documentar `GOOGLE_API_KEY` |
| `frontend/package.json` | `recharts`, `html2canvas`, `prettier`, `eslint-plugin-jsx-a11y`; scripts `lint`/`format`/`type-check` |
| `frontend/tsconfig.json` | `strict: true`, `noUncheckedIndexedAccess: true` (se não presente) |
| `frontend/.eslintrc.*` | Adicionar regras endurecidas (§2.6.2) |
| `frontend/src/App.tsx` (router) | Registrar rota `/assistente` com guarda |
| `frontend/src/components/Layout.tsx` (Navbar) | Link "Assistente" |
| `docker-compose.yml` | Passar `GOOGLE_API_KEY` via `environment:` |
| `README.md` | Seção "Assistente de Análise" + instruções de tooling e `GOOGLE_API_KEY` |

---

## 15. Plano de testes automatizados (backend, semi-TDD)

### 15.1 Abordagem

- **Framework:** pytest + httpx (já em uso)
- **Semi-TDD:** para cada módulo novo, escrever testes **antes** da implementação, começando pelos casos mais críticos (guardrail → anonymizer → endpoint integration)
- **Ordem:** (1) guardrail → (2) anonymizer → (3) readonly_db → (4) retry → (5) endpoint (integração, com mock do agente)
- **Mock do LLM:** zero chamadas reais ao Gemini em testes. Usar `monkeypatch` ou fixture para substituir `agent.run` por função canned
- **Banco de teste:** seguir padrão existente (SQLite em memória via fixture)
- **Convenções:** ver §2.5.4

### 15.2 Cobertura alvo por módulo

| Módulo | Cobertura | Prioridade |
|---|---|---|
| `sql_guardrail.py` | ≥ 95% | **Crítica** |
| `anonymizer.py` | ≥ 95% | **Crítica** |
| `readonly_db.py` | ≥ 80% | Alta |
| `routers/assistente.py` | ≥ 80% | Alta |
| `services/assistente_service.py` | ≥ 80% | Alta |
| `services/retry.py` | ≥ 80% | Média |
| `agents/*.py` | N/A (LLM) | Fora de escopo |

### 15.3 Lista completa de testes

**`tests/test_sql_guardrail.py`**
```
test_allow_valid_select
test_block_insert
test_block_update
test_block_delete
test_block_drop
test_block_alter
test_block_create_table
test_block_truncate
test_block_multiple_statements                # "SELECT 1; DROP TABLE x;"
test_block_uppercase_and_lowercase_ddl
test_block_usuarios_in_from
test_block_usuarios_in_join
test_block_usuarios_in_subquery
test_block_usuarios_case_insensitive
test_inject_limit_when_missing
test_respect_existing_limit_within_max        # LIMIT 50 → LIMIT 50
test_cap_limit_above_max                      # LIMIT 5000 → LIMIT 1000
test_malformed_sql_raises
test_empty_sql_raises
test_non_select_expression_raises             # EXPLAIN, PRAGMA, etc.
```

**`tests/test_anonymizer.py`**
```
test_no_masking_when_disabled
test_hash_nome_consumidor_deterministic
test_hash_nome_vendedor_deterministic
test_different_names_produce_different_hashes
test_mask_prefixo_cep
test_redact_comentario_truncates_and_masks_numbers
test_preserves_non_pii_columns
test_handles_null_values
test_handles_empty_rows_list
test_column_order_independence
test_mismatched_row_length_raises             # zip(strict=True) catch
```

**`tests/test_readonly_db.py`**
```
test_readonly_engine_executes_select
test_readonly_engine_rejects_insert
test_readonly_engine_rejects_update
test_readonly_engine_rejects_delete
test_missing_database_file_raises
```

**`tests/test_retry.py`**
```
test_succeeds_on_first_attempt
test_succeeds_on_second_attempt
test_succeeds_on_third_attempt
test_fails_after_max_retries
test_passes_error_context_to_next_attempt
```

**`tests/test_assistente_endpoint.py`** (integração, com mock de agente)
```
test_unauthenticated_returns_401
test_viewer_returns_403
test_admin_can_post_valid_question
test_response_shape_matches_contract
test_sql_gerado_is_returned
test_visualizacoes_contains_tabela_by_default
test_grafico_included_when_agent_suggests
test_grafico_omitted_for_single_row_result
test_tabela_omitted_when_user_asks_only_chart
test_anonimizacao_flag_masks_pii_fields
test_anonimizacao_off_preserves_original_data
test_off_topic_question_returns_friendly_error
test_guardrail_rejected_query_returns_400
test_malformed_request_returns_422
test_missing_google_api_key_returns_503
test_retry_logic_recovers_from_first_failure
test_fallback_message_after_max_retries
test_limit_forced_on_query_without_limit
```

### 15.4 Fixtures compartilhadas (em `conftest.py`)

- `test_db` — SQLite em memória com seed mínimo
- `admin_client` — `TestClient` autenticado como admin
- `viewer_client` — idem viewer
- `mock_sql_agent` — canned responses (parametrizável)
- `mock_insight_agent` — resposta canned

### 15.5 Comandos
```bash
cd backend
pytest tests/ -v
pytest tests/test_sql_guardrail.py -v
pytest --cov=app --cov-report=term-missing
```

---

## 16. Critérios de aceite

A feature é considerada pronta quando **todos** os itens abaixo são verdadeiros.

### 16.1 Funcionais
- [ ] Rota `/assistente` acessível para admin e viewer autenticados
- [ ] Viewer vê UI mas não consegue enviar (input desabilitado + 403 em POST)
- [ ] Admin consegue fazer as 10 perguntas-exemplo do PDF
- [ ] ≥ 9 de 10 perguntas-exemplo retornam SQL semanticamente correto
- [ ] Tabela renderizada por padrão em respostas não-vazias
- [ ] Gráfico renderizado quando apropriado
- [ ] Toggle 🔒 mascara PII deterministicamente
- [ ] "Ver SQL gerado" exibe a query
- [ ] Histórico de 10 via localStorage + "Limpar"
- [ ] Perguntas sugeridas funcionais
- [ ] Export CSV válido
- [ ] Export PNG legível
- [ ] Off-topic → recusa amigável
- [ ] Query maliciosa bloqueada
- [ ] Tentativa de ler `usuarios` bloqueada
- [ ] Retry recupera de falha
- [ ] Fallback amigável após 3 falhas
- [ ] Dark mode 100% funcional
- [ ] Responsivo em mobile (≥ 360px)
- [ ] Funciona com `docker compose up --build`
- [ ] Funciona com inicialização manual
- [ ] README atualizado

### 16.2 Qualidade de código — OBRIGATÓRIOS
- [ ] `ruff format --check .` sem diff
- [ ] `ruff check .` retorna 0 issues
- [ ] `mypy app/` passa 100% em strict mode
- [ ] `pytest tests/ -v` passa 100% (existentes + novos)
- [ ] Cobertura ≥ 80% nos módulos novos do backend
- [ ] Docstrings em ≥ 90% da API pública
- [ ] `npm run lint` sem warnings
- [ ] `npm run type-check` sem erros
- [ ] `npm run format:check` sem diff
- [ ] Nenhuma função backend com complexidade > 10
- [ ] Nenhum módulo backend > 300 linhas
- [ ] Nenhum componente React > 150 linhas
- [ ] Zero `any` explícito no frontend
- [ ] Zero `print()` no backend (apenas `logging`)
- [ ] Zero `os.getenv()` fora de `config.py`

---

## 17. Fora de escopo (non-goals)

Não implementar sem renegociar escopo:

- ❌ Memória de conversa / follow-ups contextuais
- ❌ Streaming de resposta (SSE)
- ❌ Persistência de histórico em banco
- ❌ Compartilhar consulta com outro usuário
- ❌ Feedback 👍/👎
- ❌ Favoritar consultas
- ❌ Agendar consultas recorrentes
- ❌ Indicador de progresso por etapa
- ❌ Anonimização de cidade ou ID
- ❌ Views SQL anonimizadas no banco
- ❌ Base de dados duplicada / ETL
- ❌ Rate limiting por usuário
- ❌ Testes de frontend (Jest/Vitest)
- ❌ Testes que chamam Gemini real
- ❌ Gráficos compostos (dual-axis, stacked)
- ❌ Filtros interativos no resultado

---

## 18. Backlog de implementação

> Ordenado por dependência. Cada tarefa é atômica, com critério de "pronto" explícito.
> **Todas as tarefas assumem aderência a §2.5 como pré-condição para "pronto".**
> **Portões de refactor** ao fim de cada fase obrigam rodar os gates de §16.2 antes de avançar.

### Fase 0 — Ferramental (antes de qualquer código de feature)

- **TASK-00** — Configurar ferramental backend: criar `backend/pyproject.toml` com config de §2.6.1; adicionar `ruff` e `mypy` em `requirements.txt`; rodar `pip install -r requirements.txt`; documentar comandos de verificação no README.
  - **Pronto quando:** `ruff check .` e `mypy app/` executam sobre o código existente sem erros (ajustando o que aparecer).

- **TASK-00b** — Configurar ferramental frontend: criar `.prettierrc` (§2.6.2); instalar `prettier`, `eslint-plugin-jsx-a11y`; endurecer regras ESLint; adicionar scripts `lint`, `format`, `format:check`, `type-check` ao `package.json`; garantir `tsconfig.json` com `strict: true`.
  - **Pronto quando:** `npm run lint`, `npm run type-check`, `npm run format:check` rodam sobre o código existente sem erros (ajustando o que aparecer).

### Fase 1 — Fundação backend (guardrails e serviços de base)

- **TASK-01** — Adicionar `pydantic-ai`, `google-genai`, `sqlglot` ao `requirements.txt`. Rodar `pip install`.
  - **Pronto quando:** `pip freeze` mostra os pacotes.

- **TASK-02** — Escrever `tests/test_sql_guardrail.py` com todos os testes de §15.3 (estado vermelho).
  - **Pronto quando:** `pytest tests/test_sql_guardrail.py` coleta e falha.

- **TASK-03** — Implementar `app/services/sql_guardrail.py` seguindo exatamente a estrutura de §10.2 (com docstrings, `Final`, funções privadas).
  - **Pronto quando:** testes passam 100%; `ruff check` e `mypy` limpos no módulo.

- **TASK-04** — Escrever `tests/test_anonymizer.py` (§15.3).
  - **Pronto quando:** testes coletam e falham.

- **TASK-05** — Implementar `app/services/anonymizer.py` conforme §13.1.
  - **Pronto quando:** testes passam 100%; gates de qualidade limpos.

- **TASK-06** — Escrever `tests/test_readonly_db.py` (§15.3).
  - **Pronto quando:** testes coletam e falham.

- **TASK-07** — Implementar `app/services/readonly_db.py` conforme §10.1.
  - **Pronto quando:** testes passam 100%; gates limpos.

- **TASK-08** — Escrever `tests/test_retry.py` (§15.3) e implementar `app/services/retry.py` com função `run_with_retry` tipada e testável.
  - **Pronto quando:** testes passam 100%; gates limpos.

- **🚦 Gate de Fase 1:** rodar `ruff check .`, `mypy app/`, `pytest tests/ -v`, `pytest --cov=app`. Todos verdes. Revisar tamanho de módulos (≤ 300 linhas) e funções (≤ 40 linhas).

### Fase 2 — Agente e endpoint

- **TASK-09** — Criar `app/agents/schema_context.py` com constante `SCHEMA_BLOCK: Final[str]`.
  - **Pronto quando:** import funciona; gates limpos.

- **TASK-10** — Criar `app/schemas/assistente.py` conforme §11.2.
  - **Pronto quando:** `pydantic.TypeAdapter` valida cada model; gates limpos.

- **TASK-11** — Criar `app/agents/sql_agent.py` (PydanticAI + `gemini-2.5-flash` + system prompt de §12.1).
  - **Pronto quando:** smoke test manual retorna `SqlGenerationResult` válido; gates limpos. *Nota: consultar docs atuais de PydanticAI para API exata.*

- **TASK-12** — Criar `app/agents/insight_agent.py` conforme §12.2.
  - **Pronto quando:** smoke test manual retorna texto coerente; gates limpos.

- **TASK-13** — Atualizar `app/config.py` com `google_api_key: str | None` via `BaseSettings`. Atualizar `.env.example`.
  - **Pronto quando:** app sobe com e sem a variável; health check reflete status.

- **TASK-14** — Criar `app/errors.py` com `register_exception_handlers(app)` para `QueryNotAllowedError`, `AgentFailureError` etc. Registrar em `main.py`.
  - **Pronto quando:** handler converte exceções em JSON correto.

- **TASK-15** — Escrever `tests/test_assistente_endpoint.py` (§15.3) com `mock_sql_agent` e `mock_insight_agent`.
  - **Pronto quando:** testes coletam e falham.

- **TASK-16** — Implementar `app/services/assistente_service.py` (orquestrador puro, sem FastAPI) com função async `responder_pergunta(pergunta, anonimizar, sql_agent, insight_agent, engine) -> RespostaAssistente`.
  - **Pronto quando:** lógica de orquestração completa e usada pelo router.

- **TASK-17** — Implementar `app/routers/assistente.py` com endpoints `POST /perguntar` e `GET /saude`, auth guard, DI de serviços/agentes via `Depends`. Zero lógica de negócio aqui.
  - **Pronto quando:** todos os testes de TASK-15 passam; gates limpos.

- **TASK-18** — Registrar `assistente.router` em `main.py`; chamar `register_exception_handlers(app)`.
  - **Pronto quando:** `GET /api/assistente/saude` → 200.

- **🚦 Gate de Fase 2:** gates completos + revisão de separação de camadas (nenhum SQL no router, nenhum `HTTPException` em service, nenhum model SQLAlchemy em response).

### Fase 3 — Frontend base

- **TASK-19** — Instalar `recharts` e `html2canvas`.
  - **Pronto quando:** `npm install` ok.

- **TASK-20** — Criar `src/types/assistente.ts` espelhando §11.2.
  - **Pronto quando:** tipos importáveis; `type-check` limpo.

- **TASK-21** — Criar `src/api/assistenteApi.ts` com função tipada `perguntarAoAssistente`.
  - **Pronto quando:** chamada manual retorna resposta válida; gates limpos.

- **TASK-22** — Criar `src/pages/AssistentePage.tsx` com layout e rota registrada. Guarda: redirect para login se não autenticado.
  - **Pronto quando:** `/assistente` renderiza para admin e viewer.

- **TASK-23** — Implementar `PromptInput.tsx` (perfil aware) e `ErrorMessage.tsx`.
  - **Pronto quando:** viewer vê input desabilitado; admin envia; erros renderizam.

- **TASK-24** — Implementar `ResultRenderer.tsx`, `DynamicTable.tsx`, `DynamicChart.tsx` + 5 wrappers em `charts/`.
  - **Pronto quando:** "Top 10 produtos" renderiza tabela + bar chart corretos.

- **TASK-25** — Implementar `SQLViewer.tsx` (colapsável).
  - **Pronto quando:** toggle expande/colapsa.

- **🚦 Gate de Fase 3:** gates de frontend limpos + cada componente ≤ 150 linhas + zero `any`.

### Fase 4 — Frontend UX extras

- **TASK-26** — Implementar `SampleQuestions.tsx` com os 10 exemplos do PDF.
  - **Pronto quando:** cards funcionais.

- **TASK-27** — Implementar `useLocalHistory.ts` + `HistorySidebar.tsx`.
  - **Pronto quando:** histórico persiste; botão "Limpar" funciona.

- **TASK-28** — Implementar `AnonymizeToggle.tsx` + passagem do flag.
  - **Pronto quando:** toggle mascara nomes.

- **TASK-29** — Botão "⬇ CSV" em `DynamicTable`.
  - **Pronto quando:** download funciona.

- **TASK-30** — Botão "⬇ PNG" em `DynamicChart` via `html2canvas`.
  - **Pronto quando:** imagem baixada está legível.

- **TASK-31** — Link "Assistente" na navbar.
  - **Pronto quando:** navegação funciona de qualquer página.

- **🚦 Gate de Fase 4:** gates de frontend limpos.

### Fase 5 — Polimento, integração e documentação

- **TASK-32** — Validar dark mode em toda a página; ajustar cores do Recharts via tokens.
  - **Pronto quando:** toggle de tema funciona.

- **TASK-33** — Validar responsividade mobile (≥ 360px).
  - **Pronto quando:** DevTools mobile ok.

- **TASK-34** — Atualizar `docker-compose.yml` com `GOOGLE_API_KEY`.
  - **Pronto quando:** container sobe com a var.

- **TASK-35** — Atualizar `README.md` com: seção da feature, instruções de `GOOGLE_API_KEY`, comandos de tooling (`ruff`, `mypy`, `npm run lint/type-check/format`), lista de perguntas de exemplo, nota sobre guardrails e anonimização.
  - **Pronto quando:** README reflete a feature e o ferramental.

- **TASK-36** — Smoke test manual das 10 perguntas do PDF.
  - **Pronto quando:** ≥ 9 de 10 ok.

- **TASK-37** — Validar execução sem Docker (seção existente do README).
  - **Pronto quando:** backend e frontend sobem manualmente e a feature funciona.

- **🚦 Gate final:** TODOS os gates de §16 verdes; revisão de aderência a §2.5 em todo o código novo.

---

## 19. Riscos e mitigações

| Risco | Impacto | Mitigação |
|---|---|---|
| Gemini gera SQL inválido para perguntas complexas | Sucesso < 90% | Retry × 2 + fallback; prompt detalhado com exemplos |
| `sqlglot` não detecta variante de DDL | Violação | Defesa em camadas: engine read-only é garantia final |
| `GOOGLE_API_KEY` ausente em produção | App quebra | Endpoint 503 + health check + documentação |
| PydanticAI tem API diferente | Retrabalho | Consultar docs durante TASK-11; código isolado no agente |
| Alucinação do insight agent | Dados incorretos | Prompt anti-alucinação; gatilho restrito |
| Gates de qualidade levantam muitos issues no código existente | Atraso na Fase 0 | Fazer em TASK-00/00b com ignore temporário por diretório; endurecer só nos módulos novos |
| Custos de Gemini escalam | Orçamento | Flash é barato (~$0.002/consulta); monitorar |
| localStorage lotado | UX | Cap 10 itens no hook |
| Tabelas grandes travam UI | UX | `LIMIT 1000` + virtualização opcional (fase 2) |

---

## 20. Referências

- PDF da atividade: `/mnt/user-data/uploads/Atividade_GenAI_-___Rocket_Lab_26_1_Perfis_v_dev_.pdf`
- Repositório: https://github.com/MathhAraujo/RocketLab-2026-GenAI
- PydanticAI: https://ai.pydantic.dev
- Gemini API: https://ai.google.dev/gemini-api/docs
- Recharts: https://recharts.org
- sqlglot: https://sqlglot.com
- ruff: https://docs.astral.sh/ruff
- mypy: https://mypy.readthedocs.io
- SQLite read-only URI: https://sqlite.org/uri.html
- Google Python Style Guide (docstrings): https://google.github.io/styleguide/pyguide.html

---

**Fim do PRD v1.2.**
