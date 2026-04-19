import type { JSX } from 'react';

type EntradaHistorico = {
  pergunta: string;
  timestamp: number;
};

type HistorySidebarProps = {
  historico: EntradaHistorico[];
  onPick: (pergunta: string) => void;
  onLimpar: () => void;
  onClose?: () => void;
};

export default function HistorySidebar({
  historico,
  onPick,
  onLimpar,
  onClose,
}: HistorySidebarProps): JSX.Element {
  return (
    <div className="flex h-full flex-col gap-2">
      <div className="flex items-center justify-between">
        <p className="text-xs font-semibold uppercase tracking-wide text-gray-400 dark:text-gray-500">
          Histórico
        </p>
        {onClose && (
          <button
            type="button"
            onClick={onClose}
            aria-label="Fechar histórico"
            className="md:hidden rounded p-1 text-gray-500 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-400 dark:text-gray-400 dark:hover:bg-gray-700"
          >
            ✕
          </button>
        )}
      </div>

      <ul className="flex flex-1 flex-col gap-1 overflow-y-auto">
        {historico.length === 0 && (
          <li className="text-xs text-gray-400 dark:text-gray-600">Nenhuma pergunta ainda.</li>
        )}
        {historico.map((entrada) => (
          <li key={entrada.timestamp}>
            <button
              type="button"
              onClick={() => onPick(entrada.pergunta)}
              className="w-full truncate rounded px-2 py-1 text-left text-xs text-gray-700 transition-colors hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-400 dark:text-gray-300 dark:hover:bg-gray-800"
              title={entrada.pergunta}
            >
              {entrada.pergunta}
            </button>
          </li>
        ))}
      </ul>

      {historico.length > 0 && (
        <button
          type="button"
          onClick={onLimpar}
          className="mt-1 rounded px-2 py-1 text-xs text-red-500 transition-colors hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-red-400 dark:hover:bg-red-900/20"
        >
          Limpar
        </button>
      )}
    </div>
  );
}
