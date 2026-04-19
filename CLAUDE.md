# CLAUDE.md

Guia de trabalho do Claude Code neste repositório. Leia antes de qualquer edição.

## Contexto do projeto

Aplicação fullstack de Gerenciamento de E-Commerce (Rocket Lab 2026). Atualmente implementando a feature `/assistente` — dashboard com agente Text-to-SQL (PydanticAI + Gemini 2.5 Flash) para consultas em linguagem natural sobre o banco.

**Documentos de referência (leia na ordem):**
1. `PRD-assistente.md` — especificação completa da feature em andamento
2. `todo-list.md` — backlog com checkboxes; fonte de verdade do que está pronto e o que falta

## Prioridade máxima: legibilidade e boas práticas

Qualidade de código vem antes de velocidade. Um módulo funcional mas ilegível é refatorado antes do merge. Se houver conflito entre "entregar mais rápido" e "entregar com qualidade", qualidade vence. Isso não é negociável.

## Fluxo de trabalho por tarefa

1. Ler `todo-list.md` e identificar a próxima tarefa desmarcada
2. Reler a seção do PRD referenciada pela tarefa (não reler o PRD inteiro)
3. Para tarefas de código com testes (Fase 1 e 2): escrever testes primeiro, confirmar que falham, depois implementar
4. Executar os gates de qualidade abaixo
5. Parar e mostrar o diff — aguardar aprovação do usuário antes de marcar `[x]` e prosseguir
6. Uma tarefa por turno. Nunca pular tarefas. Nunca executar múltiplas em lote sem pedir permissão.
7. Ao finalizar uma fase completa, gerar uma mensagem de commit sugerida (seguindo Conventional Commits em pt-BR) e aguardar autorização explícita do usuário antes de prosseguir para a próxima fase.

## Gates de qualidade (rodar antes de marcar qualquer tarefa como pronta)

```bash
# Backend
cd backend
ruff format --check .
ruff check .
mypy app/
pytest tests/ -v
pytest --cov=app --cov-report=term-missing   # só nas tarefas de implementação

# Frontend
cd frontend
npm run lint
npm run type-check
npm run format:check
```

Nenhum gate pode retornar erro, warning ou diff. Cobertura mínima de 80% em módulos novos. Se um gate falhar, corrigir antes de marcar concluído.

## Regras invioláveis

1. **Zero `print()`** no backend — use `logging.getLogger(__name__)`
2. **Zero `os.getenv()`** fora de `backend/app/config.py` — toda config passa por `BaseSettings`
3. **Zero `any`** explícito no frontend TypeScript
4. **Zero `except:` bare** e zero `except Exception:` sem re-raise ou handle específico
5. **Zero magic numbers** — extraia para constante `Final` no topo do módulo
6. **Type hints** em todas as funções Python (sintaxe moderna 3.11+: `list[str]`, `X | None`, nunca `Optional[X]`)
7. **Docstrings Google-style** obrigatórias em módulos e API pública do backend
8. **Funções ≤ 40 linhas**, módulos ≤ 300 linhas, componentes React ≤ 150 linhas, complexidade ciclomática ≤ 10
9. **Separação de camadas** — routers não contêm SQL; serviços não importam FastAPI; `HTTPException` só em routers e handlers
10. **SELECT-only no agente** — qualquer query gerada passa por `validate_and_harden()` antes de executar; tabela `usuarios` é blacklisted
11. **Nunca alterar decisões** do PRD (§3) ou padrões de código (§2.5) sem consultar o usuário

## O que NÃO fazer

- Não criar arquivos fora do que está especificado no PRD §14
- Não adicionar dependências novas além das listadas no PRD §2.1–§2.2
- Não escrever testes de frontend nem testes que chamem Gemini real
- Não implementar itens do non-goals (PRD §17)
- Não pular a Fase 0 (ferramental) — ela vem antes de qualquer código de feature
- Não usar `git commit` automaticamente; commits são decisão do usuário
- Não deletar arquivos existentes sem permissão explícita
- Não executar migrations ou `seed.py` sem permissão

## Comandos úteis do projeto

```bash
# Subir com Docker
docker compose up --build

# Backend manual
cd backend && source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Frontend manual
cd frontend && npm run dev

# Rodar só um teste específico
cd backend && pytest tests/test_sql_guardrail.py::test_block_insert -v
```

## Estrutura do repositório (resumo)

```
backend/
├── app/
│   ├── agents/           # NOVO (Fase 2) — PydanticAI agents
│   ├── services/         # NOVO — guardrail, anonymizer, readonly_db, retry, orquestrador
│   ├── routers/          # assistente.py é novo
│   ├── schemas/          # assistente.py é novo
│   ├── errors.py         # NOVO — exception handlers
│   ├── config.py         # existente — adicionar google_api_key
│   └── main.py           # existente — registrar router + handlers
├── tests/                # pytest + httpx; novos arquivos de test_*
└── pyproject.toml        # NOVO — ruff + mypy strict

frontend/
├── src/
│   ├── pages/            # AssistentePage.tsx é novo
│   ├── components/assistente/   # NOVO — todos os componentes da feature
│   ├── hooks/            # useLocalHistory.ts é novo
│   ├── api/              # assistenteApi.ts é novo
│   └── types/            # assistente.ts é novo
└── .prettierrc           # NOVO
```

## Idioma

- Código, identificadores, docstrings: inglês
- Mensagens de erro ao usuário final, UI, system prompts do agente: português do Brasil
- Commits e PRs: português do Brasil
- Comentários explicando o porquê: português do Brasil é preferível

## Variável de ambiente crítica

`GOOGLE_API_KEY` deve estar em `backend/.env`. Sem ela, o endpoint `/api/assistente/perguntar` retorna 503. Nunca logar essa variável. Nunca commitá-la.
