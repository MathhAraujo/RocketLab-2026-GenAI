# todo-list.md — Feature `/assistente` (RocketLab-2026-GenAI)

Este arquivo é a fonte de verdade da implementação. Para cada ciclo: (1) reler o bloco "Regras invioláveis";
(2) executar a próxima tarefa desmarcada na ordem em que aparece; (3) marcar `[x]` apenas após rodar todos os
comandos da seção "Gates de qualidade" com sucesso; (4) fazer commit atômico com mensagem referenciando o ID
da tarefa (`TASK-NN: ...`); (5) seguir para a próxima. Gates de fase (`🚦`) são obrigatórios — não inicie a
fase seguinte antes de marcar o gate anterior.

## Suposições

- [ ] Não aplicável — ler antes de começar:
  - A estrutura `backend/app/{routers,services,schemas,agents}` e `frontend/src/{api,components,hooks,pages,types}`
    é criada sob demanda caso ainda não exista; `__init__.py` é adicionado em novos pacotes Python.
  - `pytest` e `pytest-cov` já estão instalados no backend (assumido pelo PRD em §15); se faltarem, adicioná-los
    em `requirements.txt` durante TASK-00.
  - Não existe `backend/pyproject.toml` prévio — TASK-00 cria o arquivo do zero.
  - Script `format:check` em `package.json` usa `prettier --check src`.
  - Commits são por tarefa, em branch dedicada à feature; a branch está limpa antes de começar TASK-00.

---

## Regras invioláveis (reler antes de CADA tarefa)

- Legibilidade e boas práticas são prioridade nº 1. Em conflito entre velocidade e qualidade, qualidade vence.
- Type hints obrigatórios em toda função/método/atributo; sintaxe moderna (`list[str]`, `X | None`). Zero `any`
  no TS; `Any` no Python só com `# noqa` + justificativa.
- Docstrings Google-style em módulos e API pública do backend; docstrings auto-explicativas quando possível.
- Zero magic numbers — extrair para constante `UPPER_SNAKE_CASE` com `Final`; compartilhadas em `app/core/constants.py`.
- Separação de camadas: router só faz HTTP/auth/DI; service tem lógica de negócio e **não** importa FastAPI;
  modelos SQLAlchemy nunca são retornados como response.
- Exceções: nunca `except:` ou `except Exception:` bare; sempre `raise X from e`; mensagens ao usuário em pt-BR.
- Config: zero `os.getenv()` fora de `app/config.py` (usar `BaseSettings` + `Depends(get_settings)`).
- Logging: `logger = logging.getLogger(__name__)`; zero `print()`; nunca logar `GOOGLE_API_KEY` nem PII quando
  `anonimizar=True`.
- Limites: função ≤ 40 linhas (alvo 20); módulo Python ≤ 300 (alvo 200); componente React ≤ 150; complexidade
  ciclomática ≤ 10.
- Testes: AAA explícito; nomes `test_<subject>_<condition>_<expected>`; mocks só em fronteiras externas (LLM/rede).

---

## Gates de qualidade (rodar TUDO antes de marcar qualquer tarefa como concluída)

Backend (em `backend/`):

```bash
ruff format --check .
ruff check .
mypy app/
pytest tests/ -v
pytest --cov=app --cov-report=term-missing
```

Frontend (em `frontend/`):

```bash
npm run lint
npm run type-check
npm run format:check
```

Critérios numéricos:

- `ruff check` e `ruff format --check`: zero diffs / issues.
- `mypy app/`: zero erros em modo strict.
- `pytest`: 100% verde.
- Cobertura ≥ 80% nos módulos novos (≥ 95% em `sql_guardrail.py` e `anonymizer.py`).
- `npm run lint`: zero warnings. `npm run type-check`: zero errors. `npm run format:check`: sem diff.
- Nenhuma função backend com complexidade > 10; nenhum módulo > 300 linhas; nenhum componente React > 150 linhas.

---

## Referências rápidas (mapa tarefa → seção do PRD)

- TASK-00 / TASK-00b → §2.5, §2.6 (ferramental e padrões de código)
- TASK-01 → §2.1, §2.2 (dependências novas)
- TASK-02 / TASK-03 → §10.2 (guardrail) + testes em §15.3
- TASK-04 / TASK-05 → §13.1 (anonymizer) + testes em §15.3
- TASK-06 / TASK-07 → §10.1 (readonly engine) + testes em §15.3
- TASK-08 → §7.4 (retry) + testes em §15.3
- TASK-09 → §4 (schema do banco) e §12.1 (prompt que consome `SCHEMA_BLOCK`)
- TASK-10 → §11.2 (schemas Pydantic)
- TASK-11 → §12.1 (system prompt SQL agent) e §8.3
- TASK-12 → §12.2 (system prompt insight agent) e §8.3
- TASK-13 → §2.3 (env vars) e §11.3 (health)
- TASK-14 → §2.5.2 "Exceções e erros" + §11.1 (status HTTP)
- TASK-15 / TASK-16 / TASK-17 / TASK-18 → §7.1, §8.2, §11.1, §15.3, §15.4
- TASK-19 → §2.2 (frontend deps)
- TASK-20 → §11.2 (espelho dos schemas)
- TASK-21 → §2.5.3 "Tipagem de API"
- TASK-22 → §5, §8.1 (layout e guardas de perfil)
- TASK-23 → §5.1, §8.1
- TASK-24 → §7.2, §7.3, §8.1
- TASK-25 → §8.1 (SQLViewer)
- TASK-26 → §6 US-09, §8.1 (SampleQuestions)
- TASK-27 → §7.6 (localStorage)
- TASK-28 → §7.5, §13 (anonimização)
- TASK-29 / TASK-30 → §6 US-08 (exportação)
- TASK-31 → §8.1 (Navbar)
- TASK-32 / TASK-33 → §9.2 (dark mode, responsividade)
- TASK-34 → §2.3, §9.2 (Docker)
- TASK-35 → §14.3 (README)
- TASK-36 / TASK-37 → §9.2, §16.1
- Critérios de aceite finais → §16.1 e §16.2

---

## Fase 0 — Ferramental (antes de qualquer código de feature)

### TASK-00 — Configurar ferramental backend (`ruff` + `mypy`)

Arquivos: `backend/pyproject.toml` (novo), `backend/requirements.txt`, `README.md`.

- [x] Adicionar `ruff` e `mypy` em `backend/requirements.txt` e rodar `pip install -r requirements.txt`.
- [x] Criar `backend/pyproject.toml` copiando literalmente a configuração de §2.6.1 (blocos `[tool.ruff]`,
      `[tool.ruff.lint]`, `[tool.ruff.lint.pydocstyle]`, `[tool.ruff.lint.mccabe]`,
      `[tool.ruff.lint.per-file-ignores]`, `[tool.ruff.format]`, `[tool.mypy]`, `[[tool.mypy.overrides]]`).
- [x] Rodar `ruff format .` e `ruff check . --fix` no código existente; resolver issues remanescentes.
- [x] Rodar `mypy app/` no código existente; adicionar `ignore_missing_imports` em overrides para libs sem stubs
      e corrigir erros reais de tipo.
- [x] Documentar em `README.md` os comandos padronizados de §2.6.1 numa seção "Qualidade de código — backend".

Pronto quando: `ruff check .` e `mypy app/` executam sobre o código existente sem erros
(ajustando o que aparecer).

Referência: PRD §2.5, §2.6.1, §18 Fase 0.

### TASK-00b — Configurar ferramental frontend (ESLint endurecido + Prettier)

Arquivos: `frontend/.prettierrc` (novo), `frontend/package.json`, `frontend/.eslintrc.*`, `frontend/tsconfig.json`,
`README.md`.

- [x] Instalar `prettier` e `eslint-plugin-jsx-a11y` como devDependencies via `npm install -D`.
- [x] Criar `frontend/.prettierrc` com o JSON literal de §2.6.2.
- [x] Endurecer `.eslintrc.*`: `@typescript-eslint/no-explicit-any: "error"`,
      `@typescript-eslint/explicit-module-boundary-types: "warn"`, `react-hooks/exhaustive-deps: "error"`,
      preset `plugin:jsx-a11y/recommended`.
- [x] Adicionar em `package.json` os scripts `lint`, `format`, `format:check`, `type-check` conforme §2.6.2.
- [x] Garantir em `tsconfig.json`: `"strict": true`, `"noUncheckedIndexedAccess": true`, `"noImplicitAny": true`.
- [x] Rodar `npm run lint`, `npm run type-check`, `npm run format:check` e corrigir o que aparecer.
- [x] Documentar no `README.md` os comandos em seção "Qualidade de código — frontend".

Pronto quando: `npm run lint`, `npm run type-check`, `npm run format:check` rodam sobre o código existente
sem erros (ajustando o que aparecer).

Referência: PRD §2.5.3, §2.6.2, §18 Fase 0.

### 🚦 Gate Fase 0

- [x] Todos os comandos da seção "Gates de qualidade" passam no código existente com a nova configuração.

---

## Fase 1 — Fundação backend (guardrails e serviços de base)

### TASK-01 — Adicionar dependências Python da feature

Arquivos: `backend/requirements.txt`.

- [x] Adicionar `pydantic-ai`, `google-genai`, `sqlglot` em `backend/requirements.txt` (ordem alfabética).
- [x] Rodar `pip install -r requirements.txt`.
- [x] Executar `pip freeze | grep -E 'pydantic-ai|google-genai|sqlglot'` e confirmar presença.

Pronto quando: `pip freeze` mostra os pacotes.

Referência: PRD §2.1, §18 Fase 1.

### TASK-02 — Escrever testes vermelhos do SQL guardrail

Arquivos: `backend/tests/test_sql_guardrail.py` (novo).

- [x] Criar o arquivo e importar `validate_and_harden` e `QueryNotAllowedError` (imports falharão até TASK-03).
- [x] Adicionar os 20 testes listados em §15.3 para `sql_guardrail`, um por caso (SELECT válido, blocos de DDL/DML,
      `usuarios` em `FROM`/`JOIN`/`subquery`/case-insensitive, multi-statement, injeção/respeito/cap de `LIMIT`,
      SQL malformado, SQL vazio, `EXPLAIN`/`PRAGMA`).
- [x] Usar `pytest.mark.parametrize` onde houver família de casos similares (ex.: bloqueios de DDL).
- [x] Rodar `pytest tests/test_sql_guardrail.py` e confirmar estado vermelho (coleta + falhas).

Pronto quando: `pytest tests/test_sql_guardrail.py` coleta e falha.

Referência: PRD §15.3 (`tests/test_sql_guardrail.py`), §18 Fase 1.

### TASK-03 — Implementar `sql_guardrail.py`

Arquivos: `backend/app/services/sql_guardrail.py` (novo), `backend/app/services/__init__.py`.

- [x] Criar o módulo com module docstring e `from __future__ import annotations`, imports stdlib/third-party/local.
- [x] Declarar `MAX_ROWS: Final[int] = 1000` e `FORBIDDEN_TABLES: Final[frozenset[str]] = frozenset({"usuarios"})`.
- [x] Declarar exceção `QueryNotAllowedError(ValueError)` com docstring.
- [x] Implementar `validate_and_harden(sql: str) -> str` conforme §10.2, com docstring Google
      cobrindo Args/Returns/Raises.
- [x] Implementar helpers privados `_parse_single_statement`, `_ensure_select`, `_ensure_no_forbidden_tables`,
      `_enforce_limit` exatamente como §10.2.
- [x] Rodar todos os gates; confirmar testes de TASK-02 passam 100%.

Pronto quando: testes passam 100%; `ruff check` e `mypy` limpos no módulo.

Referência: PRD §10.2, §15.3, §18 Fase 1.

### TASK-04 — Escrever testes vermelhos do anonymizer

Arquivos: `backend/tests/test_anonymizer.py` (novo).

- [ ] Criar o arquivo e importar `anonymize_rows` e `PII_TRANSFORMERS` (imports falharão até TASK-05).
- [ ] Adicionar os 11 testes listados em §15.3 (disabled → no-op, hash determinístico para nomes, nomes diferentes
      → hashes diferentes, `mask_prefixo_cep`, redact de comentário, preserva não-PII, null-safe, lista vazia,
      independência de ordem de coluna, `zip(strict=True)` em desalinhamento).
- [ ] Rodar `pytest tests/test_anonymizer.py` e confirmar coleta + falha.

Pronto quando: testes coletam e falham.

Referência: PRD §15.3 (`tests/test_anonymizer.py`), §18 Fase 1.

### TASK-05 — Implementar `anonymizer.py`

Arquivos: `backend/app/services/anonymizer.py` (novo).

- [ ] Criar módulo com docstring e imports conforme §13.1; usar `collections.abc.Callable`.
- [ ] Declarar `_HASH_LENGTH: Final[int] = 6`, `_COMMENT_MAX_LENGTH: Final[int] = 40`,
      `_NUMBER_PATTERN: Final[re.Pattern[str]] = re.compile(r"\d{3,}")`.
- [ ] Implementar privados `_hash6`, `_mask_cep`, `_redact_comment`, `_hash_name` (factory) como em §13.1.
- [ ] Declarar `PII_TRANSFORMERS: Final[dict[str, Callable[[Any], Any]]]` com entradas `nome_consumidor`,
      `nome_vendedor`, `autor_resposta`, `prefixo_cep`, `comentario`, `titulo_comentario`.
- [ ] Implementar `anonymize_rows(columns, rows, enabled) -> list[list[Any]]` com docstring Google;
      usar `zip(..., strict=True)`.
- [ ] Rodar todos os gates; confirmar testes de TASK-04 passam 100%.

Pronto quando: testes passam 100%; gates de qualidade limpos.

Referência: PRD §13.1, §15.3, §18 Fase 1.

### TASK-06 — Escrever testes vermelhos do readonly engine

Arquivos: `backend/tests/test_readonly_db.py` (novo).

- [ ] Criar o arquivo e importar `get_readonly_engine` (import falhará até TASK-07).
- [ ] Adicionar os 5 testes listados em §15.3 (executa SELECT, rejeita INSERT/UPDATE/DELETE, falha se DB ausente).
- [ ] Usar fixture temporária (`tmp_path`) para criar banco mínimo em disco com uma tabela de teste.
- [ ] Rodar `pytest tests/test_readonly_db.py` e confirmar vermelho.

Pronto quando: testes coletam e falham.

Referência: PRD §15.3 (`tests/test_readonly_db.py`), §18 Fase 1.

### TASK-07 — Implementar `readonly_db.py`

Arquivos: `backend/app/services/readonly_db.py` (novo).

- [ ] Criar módulo conforme §10.1: docstring, `from __future__ import annotations`, imports.
- [ ] Implementar `get_readonly_engine(db_path: str = "./database.db") -> Engine` com `@lru_cache`,
      docstring Google, `FileNotFoundError` quando path não existe.
- [ ] Montar URI `sqlite:///file:{resolved}?mode=ro&uri=true` e `create_engine(uri, connect_args={"uri": True})`.
- [ ] Rodar todos os gates; confirmar testes de TASK-06 passam.

Pronto quando: testes passam 100%; gates limpos.

Referência: PRD §10.1, §15.3, §18 Fase 1.

### TASK-08 — Implementar `retry.py` (testes + módulo)

Arquivos: `backend/tests/test_retry.py` (novo), `backend/app/services/retry.py` (novo).

- [ ] Criar `tests/test_retry.py` com os 5 testes de §15.3 (sucesso 1ª/2ª/3ª tentativa, falha após 3, contexto
      de erro propagado à próxima tentativa) e confirmar vermelho.
- [ ] Criar `app/services/retry.py` com function `run_with_retry` async tipada
      (`Callable[..., Awaitable[T]]` + contexto de erro), `MAX_ATTEMPTS: Final[int] = 3`.
- [ ] Expor tipo `RetryContext` (Pydantic ou dataclass) contendo `sql_anterior: str | None` e
      `mensagem_erro: str | None`.
- [ ] Rodar todos os gates; confirmar testes passam 100%.

Pronto quando: testes passam 100%; gates limpos.

Referência: PRD §7.4, §15.3, §18 Fase 1.

### 🚦 Gate Fase 1

- [ ] Rodar `ruff check .`, `ruff format --check .`, `mypy app/`, `pytest tests/ -v`,
      `pytest --cov=app --cov-report=term-missing`.
- [ ] Todos verdes; cobertura ≥ 95% em `sql_guardrail.py` e `anonymizer.py`; ≥ 80% em `readonly_db.py` e
      `retry.py`.
- [ ] Revisão visual: módulos ≤ 300 linhas, funções ≤ 40 linhas, complexidade ≤ 10.

---

## Fase 2 — Agente e endpoint

### TASK-09 — Criar `schema_context.py` com `SCHEMA_BLOCK`

Arquivos: `backend/app/agents/__init__.py` (novo), `backend/app/agents/schema_context.py` (novo).

- [ ] Criar `__init__.py` vazio no pacote `agents`.
- [ ] Declarar `SCHEMA_BLOCK: Final[str]` com o schema literal de §4 (tabelas `consumidores`, `vendedores`,
      `produtos`, `pedidos`, `itens_pedidos`, `avaliacoes_pedidos`, com anotação de que `usuarios` é bloqueada).
- [ ] Incluir as observações de modelagem de §4.1 no bloco (receita total, por categoria, por estado,
      `entrega_no_prazo` string).
- [ ] Adicionar module docstring explicando que o bloco é injetado no system prompt.

Pronto quando: import funciona; gates limpos.

Referência: PRD §4, §4.1, §12.1, §18 Fase 2.

### TASK-10 — Criar `schemas/assistente.py`

Arquivos: `backend/app/schemas/assistente.py` (novo).

- [ ] Criar módulo com docstring e `from __future__ import annotations`.
- [ ] Implementar `PerguntaRequest` com `model_config = ConfigDict(extra="forbid")`, `pergunta: str` com
      `Field(min_length=3, max_length=500)`, `anonimizar: bool = False`.
- [ ] Implementar `TabelaVisualizacao` com `tipo: Literal["tabela"] = "tabela"`, `titulo`, `colunas`, `linhas`.
- [ ] Implementar `GraficoVisualizacao` com `subtipo: Literal["bar", "line", "pie", "area", "scatter"]`,
      `titulo`, `eixo_x`, `eixo_y`, `dados`.
- [ ] Declarar `Visualizacao = TabelaVisualizacao | GraficoVisualizacao` como `TypeAlias`.
- [ ] Implementar `MetadadosResposta` e `RespostaAssistente` exatamente como §11.2.
- [ ] Validar cada model com `pydantic.TypeAdapter(...).validate_python({...})` em um teste rápido descartável.

Pronto quando: `pydantic.TypeAdapter` valida cada model; gates limpos.

Referência: PRD §11.2, §18 Fase 2.

### TASK-11 — Criar `agents/sql_agent.py`

Arquivos: `backend/app/agents/sql_agent.py` (novo).

- [ ] Consultar docs atuais de PydanticAI (https://ai.pydantic.dev) para API exata antes de codificar.
- [ ] Definir `SqlGenerationResult` (Pydantic `BaseModel`) com campos `sql`, `explicacao_seca`,
      `sugestao_grafico`, `grafico_config`, `forcar_tabela`, `eh_off_topic`, `mensagem_off_topic`.
- [ ] Instanciar `Agent` PydanticAI com modelo `gemini-2.5-flash` via provider `google-gla`.
- [ ] Injetar o system prompt literal de §12.1 com `{SCHEMA_BLOCK}` substituído por
      `schema_context.SCHEMA_BLOCK`.
- [ ] Expor função pública tipada `async def gerar_sql(pergunta: str, retry_context: RetryContext | None = None)
      -> SqlGenerationResult`.
- [ ] Rodar smoke test manual: chamar a função com `"Top 10 produtos mais vendidos"` e verificar `sql` não-vazio
      e `sugestao_grafico="bar"`.

Pronto quando: smoke test manual retorna `SqlGenerationResult` válido; gates limpos.

Referência: PRD §8.3, §12.1, §18 Fase 2.

### TASK-12 — Criar `agents/insight_agent.py`

Arquivos: `backend/app/agents/insight_agent.py` (novo).

- [ ] Definir `InsightResult(BaseModel)` com `explicacao_analitica: str`.
- [ ] Instanciar `Agent` PydanticAI com `gemini-2.5-flash`.
- [ ] Injetar o system prompt literal de §12.2 (regras anti-alucinação, máx 2–4 frases).
- [ ] Expor `async def gerar_insight(pergunta: str, colunas: list[str], linhas_top100: list[list[Any]],
      explicacao_seca: str) -> InsightResult`.
- [ ] Smoke test manual: chamar com dados fake e verificar texto coerente e sem valores inventados.

Pronto quando: smoke test manual retorna texto coerente; gates limpos.

Referência: PRD §8.3, §12.2, §18 Fase 2.

### TASK-13 — Adicionar `GOOGLE_API_KEY` em `config.py`

Arquivos: `backend/app/config.py`, `backend/.env.example`.

- [ ] Adicionar campo `google_api_key: str | None = None` em `Settings(BaseSettings)`.
- [ ] Manter factory `get_settings()` com `@lru_cache`.
- [ ] Atualizar `backend/.env.example` com `GOOGLE_API_KEY=` e comentário explicando que sem ela o endpoint
      `/api/assistente/perguntar` retorna 503.
- [ ] Subir o app com e sem a variável definida e validar que `GET /api/assistente/saude` reflete o status
      em `gemini_configurado` (após TASK-17/18).

Pronto quando: app sobe com e sem a variável; health check reflete status.

Referência: PRD §2.3, §11.3, §18 Fase 2.

### TASK-14 — Criar `errors.py` com handlers centralizados

Arquivos: `backend/app/errors.py` (novo), `backend/app/main.py`.

- [ ] Criar exceções de domínio: `AgentFailureError`, `GeminiNotConfiguredError` (em `errors.py` ou co-localizadas
      nos módulos apropriados); `QueryNotAllowedError` já existe em `sql_guardrail.py`.
- [ ] Implementar `register_exception_handlers(app: FastAPI) -> None` que registra handlers convertendo
      `QueryNotAllowedError` → 400 `{"erro":"query_rejeitada","motivo":...}`, `AgentFailureError` → 500,
      `GeminiNotConfiguredError` → 503 com detail literal de §11.1.
- [ ] Logar detalhes técnicos via `logger.exception(...)` em cada handler; resposta JSON em pt-BR.
- [ ] Chamar `register_exception_handlers(app)` em `main.py` (preparar hook mesmo sem router registrado ainda).

Pronto quando: handler converte exceções em JSON correto.

Referência: PRD §2.5.2 "Exceções e erros", §11.1, §18 Fase 2.

### TASK-15 — Escrever testes de integração do endpoint

Arquivos: `backend/tests/test_assistente_endpoint.py` (novo), `backend/tests/conftest.py`.

- [ ] Adicionar em `conftest.py` as fixtures de §15.4: `test_db` (SQLite em memória com seed), `admin_client`,
      `viewer_client`, `mock_sql_agent` (parametrizável), `mock_insight_agent` (canned).
- [ ] Criar `test_assistente_endpoint.py` com os 18 testes de §15.3 (auth 401/403, shape do contrato, tabela
      por padrão, gráfico quando sugerido/omitido em unitário, modos de tabela/gráfico forçados, anonimização
      on/off, off-topic, guardrail 400, request inválido 422, `GOOGLE_API_KEY` ausente 503, retry recovery,
      fallback amigável, `LIMIT` forçado).
- [ ] Garantir que `mock_sql_agent` substitui `agent.run` via `monkeypatch`, sem chamar Gemini real.
- [ ] Rodar pytest e confirmar estado vermelho (a implementação vem na TASK-16/17/18).

Pronto quando: testes coletam e falham.

Referência: PRD §15.3 (`tests/test_assistente_endpoint.py`), §15.4, §18 Fase 2.

### TASK-16 — Implementar `assistente_service.py` (orquestrador puro)

Arquivos: `backend/app/services/assistente_service.py` (novo).

- [ ] Criar módulo com docstring e imports; **zero** import de `fastapi` (sem `HTTPException`, sem `Depends`).
- [ ] Implementar `async def responder_pergunta(pergunta: str, anonimizar: bool, sql_agent, insight_agent,
      engine: Engine) -> RespostaAssistente` conforme fluxo de §7.1.
- [ ] Encadear: gerar SQL → `validate_and_harden` → executar na engine read-only (timeout 10s) →
      `anonymize_rows` → aplicar regras de composição de §7.2 → decidir two-pass (`3 ≤ linhas ≤ 100` e
      coluna numérica) e chamar `insight_agent` quando aplicável.
- [ ] Integrar `run_with_retry` (máx 3 tentativas) injetando `RetryContext` com SQL e erro anteriores.
- [ ] Em caso de off-topic ou falha total, retornar `RespostaAssistente` com `erro_amigavel` preenchido
      (status 200 conforme §7.4).
- [ ] Aplicar heurística de gráfico de §7.3 em função privada dedicada.

Pronto quando: lógica de orquestração completa e usada pelo router.

Referência: PRD §7.1, §7.2, §7.3, §7.4, §7.5, §8.2, §18 Fase 2.

### TASK-17 — Implementar `routers/assistente.py`

Arquivos: `backend/app/routers/assistente.py` (novo).

- [ ] Criar `APIRouter(prefix="/api/assistente", tags=["assistente"])`.
- [ ] Endpoint `POST /perguntar` tipado `async def perguntar(req: PerguntaRequest, usuario=Depends(get_admin_user),
      service=Depends(get_assistente_service), ...) -> RespostaAssistente` — sem lógica de negócio, apenas DI +
      delegação + retorno.
- [ ] Endpoint `GET /saude` público retornando `{"status": "ok", "gemini_configurado": bool, "banco_acessivel": bool}`.
- [ ] Injetar `sql_agent`, `insight_agent`, `engine` via `Depends` isoladas em `app/dependencies.py` ou no
      próprio router (factory com `@lru_cache`).
- [ ] Guardar que viewer recebe 403 e não autenticado recebe 401 via `get_admin_user`.
- [ ] Rodar gates; confirmar todos os testes da TASK-15 passam.

Pronto quando: todos os testes de TASK-15 passam; gates limpos.

Referência: PRD §8.2, §11.1, §15.3, §18 Fase 2.

### TASK-18 — Registrar router e handlers em `main.py`

Arquivos: `backend/app/main.py`.

- [ ] `app.include_router(assistente.router)` no bootstrapping.
- [ ] Confirmar que `register_exception_handlers(app)` de TASK-14 continua ativo.
- [ ] Subir `uvicorn` manualmente e chamar `GET /api/assistente/saude`; validar resposta 200.

Pronto quando: `GET /api/assistente/saude` → 200.

Referência: PRD §11.3, §14.3, §18 Fase 2.

### 🚦 Gate Fase 2

- [ ] Gates completos verdes (backend).
- [ ] Revisão manual de separação de camadas: nenhum SQL cru no router, nenhum `HTTPException` em service,
      nenhum model SQLAlchemy serializado como response.
- [ ] Cobertura ≥ 80% em `routers/assistente.py`, `services/assistente_service.py`, `services/retry.py`.

---

## Fase 3 — Frontend base

### TASK-19 — Instalar libs frontend (`recharts`, `html2canvas`)

Arquivos: `frontend/package.json`, `frontend/package-lock.json`.

- [ ] Rodar `npm install recharts html2canvas`.
- [ ] Confirmar entradas em `dependencies` do `package.json`.
- [ ] Rodar `npm run lint` e `npm run type-check` para garantir nada quebrou.

Pronto quando: `npm install` ok.

Referência: PRD §2.2, §18 Fase 3.

### TASK-20 — Criar `types/assistente.ts`

Arquivos: `frontend/src/types/assistente.ts` (novo).

- [ ] Declarar `type PerguntaRequest`, `type TabelaVisualizacao`, `type GraficoVisualizacao`,
      `type Visualizacao = TabelaVisualizacao | GraficoVisualizacao`, `type MetadadosResposta`,
      `type RespostaAssistente`, espelhando exatamente os schemas de §11.2.
- [ ] Declarar `type ChartSubtipo = 'bar' | 'line' | 'pie' | 'area' | 'scatter'` e reutilizar em
      `GraficoVisualizacao`.
- [ ] Usar `type` em vez de `interface` (§2.5.3).
- [ ] Rodar `npm run type-check` para garantir zero erros.

Pronto quando: tipos importáveis; `type-check` limpo.

Referência: PRD §11.2, §2.5.3, §18 Fase 3.

### TASK-21 — Criar `api/assistenteApi.ts`

Arquivos: `frontend/src/api/assistenteApi.ts` (novo).

- [ ] Exportar função tipada `export async function perguntarAoAssistente(req: PerguntaRequest):
      Promise<RespostaAssistente>`.
- [ ] Usar `axios.post<RespostaAssistente>(...)` com interceptor de JWT já existente no projeto.
- [ ] Tratar erros HTTP retornando tipo de erro tipado (não lançar `any`).
- [ ] Validar chamada manual contra o backend rodando localmente.

Pronto quando: chamada manual retorna resposta válida; gates limpos.

Referência: PRD §2.5.3 "Tipagem de API", §18 Fase 3.

### TASK-22 — Criar `AssistentePage.tsx` e registrar rota

Arquivos: `frontend/src/pages/AssistentePage.tsx` (novo), `frontend/src/App.tsx`.

- [ ] Criar o componente container (≤ 150 linhas) com estado de `pergunta`, `anonimizar`, `resposta`, `erro`,
      `carregando`.
- [ ] Registrar a rota `/assistente` em `App.tsx`; aplicar guarda para redirecionar a login se não autenticado.
- [ ] Montar o layout de §8.1 (Navbar + grid com sidebar histórico + área principal; sidebar colapsável mobile).
- [ ] Integrar `perguntarAoAssistente` no submit.
- [ ] Validar render para admin e viewer (inputs/controles diferentes vêm em TASK-23).

Pronto quando: `/assistente` renderiza para admin e viewer.

Referência: PRD §5, §8.1, §18 Fase 3.

### TASK-23 — Implementar `PromptInput.tsx` e `ErrorMessage.tsx`

Arquivos: `frontend/src/components/assistente/PromptInput.tsx` (novo),
`frontend/src/components/assistente/ErrorMessage.tsx` (novo).

- [ ] `PromptInput.tsx` (≤ 80 linhas): textarea + botão "Enviar"; props tipadas `PromptInputProps` com
      `isAdmin`, `onSubmit`, `disabled`, `value`, `onChange`.
- [ ] Se `!isAdmin`: `disabled=true`, placeholder `"Funcionalidade restrita a administradores"`,
      tooltip `"Contate seu gestor para obter acesso de administrador"`.
- [ ] `ErrorMessage.tsx` (≤ 40 linhas): recebe `mensagem: string` e renderiza card semântico com foco visível.
- [ ] Aplicar Tailwind dark mode (`dark:` prefix) e `aria-label` onde necessário.
- [ ] Rodar gates de frontend.

Pronto quando: viewer vê input desabilitado; admin envia; erros renderizam.

Referência: PRD §5.1, §8.1, §18 Fase 3.

### TASK-24 — Implementar `ResultRenderer`, `DynamicTable`, `DynamicChart` e 5 wrappers

Arquivos: `ResultRenderer.tsx`, `DynamicTable.tsx`, `DynamicChart.tsx`,
`charts/ChartBar.tsx`, `charts/ChartLine.tsx`, `charts/ChartPie.tsx`, `charts/ChartArea.tsx`,
`charts/ChartScatter.tsx` (todos em `frontend/src/components/assistente/`).

- [ ] `ResultRenderer.tsx` (≤ 80): recebe `visualizacoes: Visualizacao[]` e mapeia para `DynamicTable` ou
      `DynamicChart` conforme `tipo` (type narrowing via `if (v.tipo === 'tabela')`).
- [ ] `DynamicTable.tsx` (≤ 120): renderiza cabeçalho + linhas; scroll horizontal em mobile.
- [ ] `DynamicChart.tsx` (≤ 80): roteia por `subtipo` para o wrapper correspondente; usa `ResponsiveContainer`.
- [ ] Criar os 5 wrappers em `charts/` (≤ 80 linhas cada) usando Recharts primitivos correspondentes.
- [ ] Aplicar dark mode (tokens Tailwind) e cores consistentes.
- [ ] Validar end-to-end: perguntar `"Top 10 produtos mais vendidos"` e confirmar tabela de 10 linhas + gráfico
      de barras correto.

Pronto quando: "Top 10 produtos" renderiza tabela + bar chart corretos.

Referência: PRD §7.2, §7.3, §8.1, §18 Fase 3.

### TASK-25 — Implementar `SQLViewer.tsx`

Arquivos: `frontend/src/components/assistente/SQLViewer.tsx` (novo).

- [ ] Componente (≤ 50 linhas) com prop `sql: string | null` e estado `expanded: boolean`.
- [ ] Botão toggle com `aria-expanded` e label `"Ver SQL gerado"` / `"Ocultar SQL"`.
- [ ] Renderizar SQL em `<pre><code>` com fonte monoespaçada e wrap apropriado.
- [ ] Integrar ao `AssistentePage` acima da `ResultRenderer`.

Pronto quando: toggle expande/colapsa.

Referência: PRD §8.1, §18 Fase 3.

### 🚦 Gate Fase 3

- [ ] `npm run lint`, `npm run type-check`, `npm run format:check` verdes.
- [ ] Cada componente ≤ 150 linhas; zero `any` explícito; zero hex hardcoded em JSX.
- [ ] Acessibilidade: labels em inputs, foco visível, HTML semântico.

---

## Fase 4 — Frontend UX extras

### TASK-26 — Implementar `SampleQuestions.tsx`

Arquivos: `frontend/src/components/assistente/SampleQuestions.tsx` (novo).

- [ ] Componente (≤ 60 linhas) com constante `SAMPLE_QUESTIONS: readonly string[]` contendo os 10 exemplos do PDF
      da atividade.
- [ ] Renderizar cards clicáveis; `onClick` preenche o input via callback prop `onPick(pergunta: string)`.
- [ ] Respeitar perfil: cards desabilitados para viewer (§5.1).
- [ ] Aplicar dark mode e `role="button"` + `aria-disabled` quando desabilitado.

Pronto quando: cards funcionais.

Referência: PRD §8.1, §6 US-09, §18 Fase 4.

### TASK-27 — Implementar `useLocalHistory.ts` e `HistorySidebar.tsx`

Arquivos: `frontend/src/hooks/useLocalHistory.ts` (novo),
`frontend/src/components/assistente/HistorySidebar.tsx` (novo).

- [ ] `useLocalHistory.ts`: hook exportando `{ historico, adicionar, limpar }`; constante
      `MAX_HISTORICO: 10`; chave `"assistente:historico"`; FIFO (truncar para 10).
- [ ] Persistir estrutura `{ pergunta: string; timestamp: number }[]` em `localStorage`.
- [ ] `HistorySidebar.tsx` (≤ 100 linhas): lista em ordem reversa cronológica; click preenche input; botão
      "Limpar" chama `limpar()`.
- [ ] Cobrir dependências de `useEffect` completas (ESLint `react-hooks/exhaustive-deps`).

Pronto quando: histórico persiste; botão "Limpar" funciona.

Referência: PRD §7.6, §8.1, §18 Fase 4.

### TASK-28 — Implementar `AnonymizeToggle.tsx`

Arquivos: `frontend/src/components/assistente/AnonymizeToggle.tsx` (novo).

- [ ] Componente (≤ 40 linhas) tipo switch com ícone 🔒; props `checked: boolean` e `onChange: (b: boolean) => void`.
- [ ] `aria-label="Modo anônimo"`; foco visível.
- [ ] Propagar o valor até o payload `anonimizar` enviado em `perguntarAoAssistente`.
- [ ] Validar end-to-end que nomes aparecem como `Consumidor_abc123` quando ativo.

Pronto quando: toggle mascara nomes.

Referência: PRD §7.5, §13, §18 Fase 4.

### TASK-29 — Botão "⬇ CSV" em `DynamicTable`

Arquivos: `frontend/src/components/assistente/DynamicTable.tsx`.

- [ ] Adicionar botão "⬇ CSV" visível para admin.
- [ ] Gerar CSV a partir de `colunas` + `linhas`, escapando aspas e vírgulas corretamente.
- [ ] Download via `Blob` + `URL.createObjectURL` + elemento `<a>` temporário.
- [ ] Arquivo com nome `{titulo-slug}-{timestamp}.csv`.

Pronto quando: download funciona.

Referência: PRD §6 US-08, §18 Fase 4.

### TASK-30 — Botão "⬇ PNG" em `DynamicChart`

Arquivos: `frontend/src/components/assistente/DynamicChart.tsx`.

- [ ] Adicionar botão "⬇ PNG" visível para admin.
- [ ] Usar `html2canvas` para capturar o container do gráfico.
- [ ] Baixar como `{titulo-slug}-{timestamp}.png`.
- [ ] Garantir cores corretas em dark e light mode antes de capturar.

Pronto quando: imagem baixada está legível.

Referência: PRD §6 US-08, §18 Fase 4.

### TASK-31 — Adicionar link "Assistente" na Navbar

Arquivos: `frontend/src/components/Layout.tsx` (ou equivalente existente).

- [ ] Adicionar `<Link to="/assistente">Assistente</Link>` na navbar.
- [ ] Estilizar consistentemente com os demais links; incluir estado ativo.
- [ ] Validar navegação a partir de qualquer página autenticada.

Pronto quando: navegação funciona de qualquer página.

Referência: PRD §8.1, §14.3, §18 Fase 4.

### 🚦 Gate Fase 4

- [ ] `npm run lint`, `npm run type-check`, `npm run format:check` verdes.
- [ ] Revisão manual das 4 extras UX (sugestões, histórico, toggle, exportação).

---

## Fase 5 — Polimento, integração e documentação

### TASK-32 — Validar dark mode em toda a página

Arquivos: componentes em `frontend/src/components/assistente/` conforme necessário.

- [ ] Alternar tema e revisar cada componente (Prompt, Sidebar, Toggle, Result, Table, Chart, SQLViewer,
      SampleQuestions, ErrorMessage).
- [ ] Ajustar cores do Recharts via props/tokens Tailwind (ex.: `stroke`, `fill` derivados de CSS vars).
- [ ] Garantir contraste WCAG AA em ambos os temas.

Pronto quando: toggle de tema funciona.

Referência: PRD §9.2, §2.5.3 "Styling", §18 Fase 5.

### TASK-33 — Validar responsividade mobile (≥ 360px)

Arquivos: componentes afetados (layout, tabela, sidebar).

- [ ] Testar em DevTools nas larguras 360px, 420px, 768px.
- [ ] Sidebar colapsa via hamburger; tabelas têm scroll horizontal; `ResponsiveContainer` em todos os gráficos.
- [ ] Nenhum overflow horizontal na página.

Pronto quando: DevTools mobile ok.

Referência: PRD §8.1, §9.2, §18 Fase 5.

### TASK-34 — Atualizar `docker-compose.yml` com `GOOGLE_API_KEY`

Arquivos: `docker-compose.yml`.

- [ ] Adicionar `GOOGLE_API_KEY: ${GOOGLE_API_KEY}` no `environment:` do serviço backend.
- [ ] Validar `docker compose up --build` com `.env` preenchido.
- [ ] Validar comportamento 503 quando `GOOGLE_API_KEY` está vazia.

Pronto quando: container sobe com a var.

Referência: PRD §2.3, §14.3, §18 Fase 5.

### TASK-35 — Atualizar `README.md`

Arquivos: `README.md`.

- [ ] Adicionar seção "Assistente de Análise" descrevendo a feature e a rota `/assistente`.
- [ ] Documentar instrução de configuração de `GOOGLE_API_KEY` (obter chave, colocar em `.env`).
- [ ] Listar comandos de tooling: `ruff format .`, `ruff check .`, `mypy app/`, `pytest`, `pytest --cov=app`,
      `npm run lint`, `npm run type-check`, `npm run format:check`.
- [ ] Listar as 10 perguntas-exemplo do PDF.
- [ ] Incluir nota explicativa sobre guardrails (SELECT-only, bloqueio de `usuarios`, `LIMIT 1000`) e
      anonimização (toggle 🔒, SHA-1 truncado).

Pronto quando: README reflete a feature e o ferramental.

Referência: PRD §14.3, §18 Fase 5.

### TASK-36 — Smoke test manual das 10 perguntas do PDF

Arquivos: nenhum (execução).

- [ ] Rodar backend e frontend com `GOOGLE_API_KEY` válida.
- [ ] Executar as 10 perguntas de exemplo; registrar sucesso/falha por item.
- [ ] Validar que ≥ 9 retornam SQL semanticamente correto e renderização adequada.
- [ ] Anotar falhas com reprodução e SQL gerado para eventuais ajustes de prompt.

Pronto quando: ≥ 9 de 10 ok.

Referência: PRD §9.2, §16.1, §18 Fase 5.

### TASK-37 — Validar execução sem Docker

Arquivos: nenhum (execução; verificar instruções do `README.md`).

- [ ] Subir backend manualmente (`uvicorn app.main:app --reload`) conforme instruções do README.
- [ ] Subir frontend manualmente (`npm run dev`).
- [ ] Fazer login como admin e repetir 2–3 perguntas-exemplo garantindo paridade com modo Docker.

Pronto quando: backend e frontend sobem manualmente e a feature funciona.

Referência: PRD §9.2, §18 Fase 5.

### 🚦 Gate Final

- [ ] TODOS os gates de §16 verdes.
- [ ] Revisão de aderência a §2.5 em todo o código novo (nomes, docstrings, constantes, camadas, tamanhos).

---

## Checklist final de aceite (§16 do PRD)

### 16.1 Funcionais

- [ ] Rota `/assistente` acessível para admin e viewer autenticados.
- [ ] Viewer vê UI mas não consegue enviar (input desabilitado + 403 em POST).
- [ ] Admin consegue fazer as 10 perguntas-exemplo do PDF.
- [ ] ≥ 9 de 10 perguntas-exemplo retornam SQL semanticamente correto.
- [ ] Tabela renderizada por padrão em respostas não-vazias.
- [ ] Gráfico renderizado quando apropriado.
- [ ] Toggle 🔒 mascara PII deterministicamente.
- [ ] "Ver SQL gerado" exibe a query.
- [ ] Histórico de 10 via `localStorage` + "Limpar".
- [ ] Perguntas sugeridas funcionais.
- [ ] Export CSV válido.
- [ ] Export PNG legível.
- [ ] Off-topic → recusa amigável.
- [ ] Query maliciosa bloqueada.
- [ ] Tentativa de ler `usuarios` bloqueada.
- [ ] Retry recupera de falha.
- [ ] Fallback amigável após 3 falhas.
- [ ] Dark mode 100% funcional.
- [ ] Responsivo em mobile (≥ 360px).
- [ ] Funciona com `docker compose up --build`.
- [ ] Funciona com inicialização manual.
- [ ] `README.md` atualizado.

### 16.2 Qualidade de código

- [ ] `ruff format --check .` sem diff.
- [ ] `ruff check .` retorna 0 issues.
- [ ] `mypy app/` passa 100% em strict mode.
- [ ] `pytest tests/ -v` passa 100% (existentes + novos).
- [ ] Cobertura ≥ 80% nos módulos novos do backend.
- [ ] Docstrings em ≥ 90% da API pública.
- [ ] `npm run lint` sem warnings.
- [ ] `npm run type-check` sem erros.
- [ ] `npm run format:check` sem diff.
- [ ] Nenhuma função backend com complexidade > 10.
- [ ] Nenhum módulo backend > 300 linhas.
- [ ] Nenhum componente React > 150 linhas.
- [ ] Zero `any` explícito no frontend.
- [ ] Zero `print()` no backend (apenas `logging`).
- [ ] Zero `os.getenv()` fora de `config.py`.
