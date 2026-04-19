# frontend/CLAUDE.md

Regras específicas do frontend. Carregado quando o Claude Code edita arquivos em `frontend/`.

## Stack

React 18 + Vite + TypeScript strict + Tailwind CSS + axios + Recharts + html2canvas + ESLint + Prettier.

## Regras TypeScript não-negociáveis

- `tsconfig.json` em strict mode total: `strict`, `noUncheckedIndexedAccess`, `noImplicitAny`
- Zero `any` explícito — use `unknown` + narrowing
- Return type explícito em toda função exportada
- Preferir `type` sobre `interface` (exceto quando extensão for essencial)
- Tipos em `src/types/assistente.ts` espelhando exatamente os schemas Pydantic do backend
- Chamadas axios sempre tipadas: `axios.post<RespostaAssistente>(url, body)`

## Componentes React

- Apenas functional components + hooks (zero class components)
- `export default` para componentes; `export` nomeado para hooks e utils
- Props com type explícito `<Component>Props` e destructuring na assinatura:

```tsx
type PromptInputProps = {
  onSubmit: (pergunta: string) => void;
  disabled: boolean;
  placeholder?: string;
};

export default function PromptInput({
  onSubmit,
  disabled,
  placeholder = 'Digite sua pergunta...',
}: PromptInputProps): JSX.Element {
  // ...
}
```

- ≤ 150 linhas por componente — ultrapassando, extrair sub-componente ou hook
- Lógica não-visual (localStorage, axios, transformação de dados) em hooks/utils, nunca no componente
- Lista em `.map()` sempre com `key` estável (não use `index` se houver ID)

## Hooks

- Prefixo `use` obrigatório
- Uma responsabilidade por hook
- Dependências de `useEffect` / `useMemo` / `useCallback` completas — ESLint `react-hooks/exhaustive-deps` está como `error`

## Styling

- 100% Tailwind. `style={{}}` inline só para valores dinâmicos inexprimíveis em classes
- Dark mode via `dark:` prefix consistente em todo componente novo
- Nunca hardcoded hex — use tokens/classes Tailwind
- Respeitar o visual do app existente (consultar componentes de `components/` antes de criar novos)

## Acessibilidade

- HTML semântico: `<button>`, `<nav>`, `<main>`, `<section>`, `<form>` — nunca `<div onClick>`
- `aria-label` em controles sem texto visível (ícones, toggles)
- `<label htmlFor>` para todo input
- Foco visível via `focus:ring-*` do Tailwind
- Contraste WCAG AA
- ESLint `jsx-a11y/*` está habilitado — respeitar os warnings

## Naming

- Componente: `PascalCase.tsx` (`PromptInput.tsx`)
- Hook: `useCamelCase.ts` (`useLocalHistory.ts`)
- Utilidade: `camelCase.ts` (`assistenteApi.ts`)
- Tipo / type alias: `PascalCase`
- Função / variável: `camelCase`
- Constante: `UPPER_SNAKE_CASE` (`const MAX_HISTORICO = 10`)
- Props type: `<Component>Props`

## Localização de código novo

```
src/
├── pages/AssistentePage.tsx             # container da rota
├── components/assistente/               # tudo relacionado à feature
│   ├── PromptInput.tsx
│   ├── SampleQuestions.tsx
│   ├── HistorySidebar.tsx
│   ├── AnonymizeToggle.tsx
│   ├── ResultRenderer.tsx
│   ├── SQLViewer.tsx
│   ├── DynamicTable.tsx
│   ├── DynamicChart.tsx
│   ├── ErrorMessage.tsx
│   └── charts/
│       ├── ChartBar.tsx
│       ├── ChartLine.tsx
│       ├── ChartPie.tsx
│       ├── ChartArea.tsx
│       └── ChartScatter.tsx
├── hooks/useLocalHistory.ts
├── api/assistenteApi.ts
└── types/assistente.ts
```

Não criar arquivos fora dessa estrutura sem consulta.

## Comandos

```bash
# Rodar sempre antes de marcar tarefa como pronta
npm run lint
npm run type-check
npm run format:check

# Auto-fix
npm run format            # Prettier
npm run lint -- --fix     # ESLint

# Dev server
npm run dev
```

Nenhum comando pode retornar warning, erro ou diff.

## Integração com backend

- Base URL vem de `VITE_API_URL` (default `http://localhost:8000/api`)
- Reutilizar o interceptor axios existente para JWT — não criar novo
- Endpoint da feature: `POST /api/assistente/perguntar`, `GET /api/assistente/saude`
- Tipos de request/response vivem em `src/types/assistente.ts` e espelham os Pydantic schemas do backend (PRD §11.2)

## Histórico local

`useLocalHistory` gerencia chave `assistente:historico` no localStorage. Máximo 10 entradas (FIFO). Botão "Limpar" faz `localStorage.removeItem`. Zero persistência no backend — esse é um non-goal explícito.

## Dark mode e responsividade

- Toda nova página/componente deve funcionar em light e dark
- Breakpoint mínimo: 360px de largura
- Sidebar colapsa em mobile (hamburger)
- Tabelas com scroll horizontal em telas estreitas
- Gráficos sempre dentro de `<ResponsiveContainer>` do Recharts

## Idioma

- Código, identificadores: inglês
- Textos visíveis ao usuário (labels, placeholders, mensagens de erro, tooltips): português do Brasil
- Comentários explicando o porquê: pt-BR é preferível
