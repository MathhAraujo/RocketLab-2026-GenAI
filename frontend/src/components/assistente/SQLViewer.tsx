import { useState } from 'react';

type SQLViewerProps = {
  sql: string | null;
};

export function SQLViewer({ sql }: SQLViewerProps): JSX.Element | null {
  const [expanded, setExpanded] = useState(false);

  if (!sql) return null;

  return (
    <div className="rounded-lg border border-gray-200 dark:border-gray-700">
      <button
        type="button"
        aria-expanded={expanded}
        onClick={() => setExpanded((prev) => !prev)}
        className="flex w-full items-center gap-2 px-3 py-2 text-left text-sm text-gray-600 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-indigo-400 dark:text-gray-400 dark:hover:bg-gray-800"
      >
        <span aria-hidden="true">{expanded ? '▾' : '▸'}</span>
        {expanded ? 'Ocultar SQL' : 'Ver SQL gerado'}
      </button>
      {expanded && (
        <pre className="overflow-x-auto border-t border-gray-200 bg-gray-50 p-3 font-mono text-xs text-gray-800 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-200">
          {sql}
        </pre>
      )}
    </div>
  );
}
