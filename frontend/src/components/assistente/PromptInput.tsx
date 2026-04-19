import type { KeyboardEvent } from 'react';

const VIEWER_PLACEHOLDER = 'Funcionalidade restrita a administradores';
const VIEWER_TOOLTIP = 'Contate seu gestor para obter acesso de administrador';
const ADMIN_PLACEHOLDER = 'Digite sua pergunta... (Enter para enviar)';

type PromptInputProps = {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  isAdmin: boolean;
  isLoading: boolean;
};

export function PromptInput({
  value,
  onChange,
  onSubmit,
  isAdmin,
  isLoading,
}: PromptInputProps): JSX.Element {
  const disabled = !isAdmin || isLoading;

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      onSubmit();
    }
  };

  return (
    <div className="flex gap-2">
      <textarea
        aria-label="Pergunta ao assistente"
        title={!isAdmin ? VIEWER_TOOLTIP : undefined}
        placeholder={isAdmin ? ADMIN_PLACEHOLDER : VIEWER_PLACEHOLDER}
        disabled={disabled}
        value={value}
        rows={2}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={handleKeyDown}
        className="min-h-[56px] flex-1 resize-none rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-400 disabled:cursor-not-allowed disabled:opacity-50 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-100 dark:placeholder-gray-500"
      />
      <button
        type="button"
        onClick={onSubmit}
        disabled={disabled || !value.trim()}
        aria-label="Enviar pergunta"
        className="self-end rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-400 disabled:cursor-not-allowed disabled:opacity-50 dark:bg-indigo-500 dark:text-white dark:hover:bg-indigo-400"
      >
        {isLoading ? '...' : 'Enviar →'}
      </button>
    </div>
  );
}
