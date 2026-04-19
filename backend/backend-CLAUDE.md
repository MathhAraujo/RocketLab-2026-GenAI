# backend/CLAUDE.md

Regras específicas do backend Python. Carregado automaticamente quando o Claude Code edita arquivos em `backend/`.

## Stack

Python 3.11+, FastAPI, SQLAlchemy 2.0, SQLite, Alembic, pytest, PydanticAI, sqlglot, ruff, mypy (strict).

## Estrutura canônica de um módulo Python novo

```python
"""Short module docstring describing responsibility."""
from __future__ import annotations

# 1. stdlib
import hashlib
from typing import Final

# 2. third-party
from pydantic import BaseModel

# 3. local
from app.schemas.assistente import PerguntaRequest

# Constants
MAX_ROWS: Final[int] = 1000

# Type aliases
Rows = list[list[object]]


# Domain exceptions
class DomainError(ValueError):
    """Raised when a domain invariant is violated."""


# Private helpers
def _helper(value: str) -> str:
    return value.lower()


# Public API
def public_function(arg: str) -> str:
    """One-line summary.

    Args:
        arg: What this argument is.

    Returns:
        What is returned.

    Raises:
        DomainError: When something is wrong.
    """
    return _helper(arg)
```

## Regras Python não-negociáveis

- Type hints em toda função/método/atributo — sintaxe 3.11+
- Sem `Optional[X]` — use `X | None`
- Sem `List[X]`, `Dict[K,V]` — use `list[X]`, `dict[K, V]`
- Sem `Any` explícito (se absolutamente necessário, `# noqa` + comentário justificando)
- `from __future__ import annotations` no topo de todo módulo novo
- Constantes de módulo com `Final` e `UPPER_SNAKE_CASE`
- `pathlib.Path` em vez de `os.path`
- f-strings (exceto em `logger.info`, que usa lazy `%s`)
- `is None` / `is not None` em comparações com None
- Nunca mutáveis default em parâmetros (`def f(x=[])` → `def f(x: list | None = None)`)
- Funções privadas (`_foo`) para extrair blocos longos

## Separação de camadas (enforce rigorosamente)

```
Router   → auth, validação Pydantic, DI. Delega tudo para serviços.
Service  → regras de negócio. NÃO importa FastAPI, NÃO levanta HTTPException.
Agent    → chamada LLM. Retorna Pydantic model tipado.
Query    → SQLAlchemy. Recebe Session, retorna dados crus ou models.
Schema   → Pydantic de request/response apenas.
Errors   → handlers centralizados em app/errors.py.
```

Checklist antes de commitar um arquivo novo:
- [ ] Se é router: não tem SQL cru, não tem lógica de negócio, só delega
- [ ] Se é service: não tem `from fastapi import ...`, não levanta `HTTPException`
- [ ] Se é schema: só tem Pydantic BaseModel, sem lógica
- [ ] Se é agent: retorna um BaseModel tipado, não um dict

## Exceções

- Definir no módulo de domínio:
  ```python
  class QueryNotAllowedError(ValueError):
      """Raised when SQL violates security guardrails."""
  ```
- Levantar com contexto: `raise QueryNotAllowedError(msg) from exc`
- Handler HTTP em `app/errors.py`, registrado via `register_exception_handlers(app)` em `main.py`
- Nunca `except:` bare; nunca `except Exception:` sem handle específico

## Testes (pytest)

- Nome do arquivo: `test_<modulo>.py`
- Nome do teste: `test_<subject>_<condition>_<expected>`
- Um conceito por teste
- AAA pattern com comentários `# Arrange / # Act / # Assert` quando ajuda clareza
- Fixtures em `conftest.py`; evite setup/teardown manual
- `pytest.mark.parametrize` para famílias de casos similares
- Zero interdependência entre testes
- Zero chamadas reais ao Gemini — mockar `agent.run` via fixture `mock_sql_agent`

## Comandos específicos

```bash
# Rodar sempre antes de marcar tarefa como pronta
ruff format --check .
ruff check .
mypy app/
pytest tests/ -v

# Cobertura (rodar ao final de cada tarefa de implementação)
pytest --cov=app --cov-report=term-missing

# Rodar um teste específico
pytest tests/test_sql_guardrail.py::test_block_insert -v

# Auto-fix de lint
ruff check . --fix
ruff format .
```

## Configuração

Tudo que vem de env var passa por `pydantic_settings.BaseSettings` em `app/config.py`. Exemplo:

```python
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    google_api_key: str | None = None

@lru_cache
def get_settings() -> Settings:
    return Settings()
```

Injete via `Depends(get_settings)` nos routers. Zero `os.getenv()` espalhado.

## Logging

```python
import logging
logger = logging.getLogger(__name__)

logger.info("query ran in %.2fs", elapsed)   # lazy formatting
```

Nunca `print()`. Nunca logar `GOOGLE_API_KEY`, senhas, ou PII quando `anonimizar=True`.

## Async / sync

- Rotas FastAPI: `async def`
- Chamadas a LLM (PydanticAI): `async def`
- Lógica pura (parser, anonymizer): `def` síncrono — não force async sem motivo
- Nunca `asyncio.run()` dentro de handlers

## Limites

- Função ≤ 20 linhas (teto 40)
- Método ≤ 15 linhas (teto 30)
- Módulo ≤ 200 linhas (teto 300)
- Classe ≤ 150 linhas (teto 250)
- Complexidade ciclomática ≤ 10 (enforced via ruff C90)

Acima do teto: refatorar antes de continuar.

## Guardrails do agente Text-to-SQL

Toda query gerada pelo agente passa por:
1. `validate_and_harden()` — parser sqlglot (rejeita não-SELECT, tabela `usuarios`, múltiplos statements; injeta LIMIT 1000)
2. Execução na engine read-only (`get_readonly_engine()`) — camada final de defesa via `mode=ro` do SQLite

Nunca permitir que o agente execute SQL sem passar pelas duas camadas. Nunca remover uma das camadas achando que a outra é suficiente.
