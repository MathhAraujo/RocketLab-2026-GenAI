# Ajustes Extras (fora do PRD)

| Data       | Descrição                                                                 | Arquivos afetados                        |
|------------|---------------------------------------------------------------------------|------------------------------------------|
| 2026-04-19 | Remove exemplos hardcoded e regras prescritivas de gráfico do system prompt do SQL agent; Gemini agora decide livremente o tipo de visualização | `backend/app/agents/sql_agent.py` |
| 2026-04-19 | Remove botão Dashboard (placeholder) e botão Novo Produto da sidebar; formulário de criação agora aparece como modal direto na página Catálogo | `Sidebar.tsx`, `CatalogoPage.tsx`, `useProdutos.ts` |
