import { useEffect, useRef, useState } from 'react';
import type { JSX } from 'react';
import type { EntradaHistorico } from '../../hooks/useLocalHistory';

type HistoryDropdownProps = {
  historico: EntradaHistorico[];
  onPick: (entrada: EntradaHistorico) => void;
  onLimpar: () => void;
};

export default function HistoryDropdown({
  historico,
  onPick,
  onLimpar,
}: HistoryDropdownProps): JSX.Element {
  const [aberto, setAberto] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const panelId = 'history-dropdown-panel';

  useEffect(() => {
    if (!aberto) return;

    const handleMouseDown = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setAberto(false);
      }
    };
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setAberto(false);
    };

    document.addEventListener('mousedown', handleMouseDown);
    document.addEventListener('keydown', handleKeyDown);
    return () => {
      document.removeEventListener('mousedown', handleMouseDown);
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [aberto]);

  const handlePick = (entrada: EntradaHistorico) => {
    setAberto(false);
    onPick(entrada);
  };

  const handleLimpar = () => {
    setAberto(false);
    onLimpar();
  };

  const label = historico.length > 0 ? `Histórico (${historico.length})` : 'Histórico';

  return (
    <div ref={containerRef} className="relative">
      <button
        type="button"
        aria-expanded={aberto}
        aria-controls={panelId}
        onClick={() => setAberto((prev) => !prev)}
        className="flex items-center gap-1 rounded-lg border border-gray-300 px-3 py-1.5 text-sm text-gray-700 transition-colors hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-400 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-800"
      >
        <span>{aberto ? '▴' : '▾'}</span>
        <span>{label}</span>
      </button>

      {aberto && (
        <div
          id={panelId}
          role="listbox"
          aria-label="Histórico de perguntas"
          className="absolute left-0 top-full z-40 mt-1 w-80 rounded-lg border border-gray-200 bg-white shadow-lg dark:border-gray-700 dark:bg-gray-900"
        >
          {historico.length === 0 ? (
            <p className="px-3 py-3 text-xs text-gray-400 dark:text-gray-600">
              Nenhuma pergunta ainda.
            </p>
          ) : (
            <>
              <ul className="max-h-60 overflow-y-auto">
                {historico.map((entrada) => (
                  <li key={entrada.timestamp} role="option" aria-selected={false}>
                    <button
                      type="button"
                      onClick={() => handlePick(entrada)}
                      title={entrada.pergunta}
                      className="w-full truncate px-3 py-2 text-left text-sm text-gray-700 transition-colors hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-indigo-400 dark:text-gray-300 dark:hover:bg-gray-800"
                    >
                      {entrada.pergunta}
                    </button>
                  </li>
                ))}
              </ul>
              <div className="border-t border-gray-100 px-3 py-2 dark:border-gray-700">
                <button
                  type="button"
                  onClick={handleLimpar}
                  className="text-xs text-red-500 transition-colors hover:text-red-700 focus:outline-none focus:ring-2 focus:ring-red-400 dark:hover:text-red-400"
                >
                  Limpar histórico
                </button>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
}
