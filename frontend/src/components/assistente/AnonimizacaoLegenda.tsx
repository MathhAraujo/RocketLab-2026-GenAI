import { useState } from 'react';

const PAGE_SIZE = 10;

type AnonimizacaoLegendaProps = {
  traducao: Record<string, string>;
};

export function AnonimizacaoLegenda({ traducao }: AnonimizacaoLegendaProps): JSX.Element {
  const [expanded, setExpanded] = useState(false);

  const entries = Object.entries(traducao);
  const visibleEntries = expanded ? entries : entries.slice(0, PAGE_SIZE);
  const remaining = entries.length - PAGE_SIZE;

  return (
    <section className="rounded-md border border-amber-200 bg-amber-50 p-3 dark:border-amber-800 dark:bg-amber-950/30">
      <p className="mb-2 text-xs font-semibold text-amber-700 dark:text-amber-300">
        Tradução da anonimização
      </p>
      <ul className="space-y-0.5">
        {visibleEntries.map(([token, real]) => (
          <li key={token} className="font-mono text-xs text-gray-700 dark:text-gray-300">
            <span className="text-amber-600 dark:text-amber-400">{token}</span>
            {' \u2192 '}
            <span>{real}</span>
          </li>
        ))}
      </ul>
      {!expanded && remaining > 0 && (
        <button
          type="button"
          onClick={() => setExpanded(true)}
          className="mt-2 w-full rounded py-1.5 text-xs text-gray-500 hover:bg-amber-100 dark:text-gray-400 dark:hover:bg-amber-900/40"
        >
          Mostrar mais ({remaining})
        </button>
      )}
    </section>
  );
}
