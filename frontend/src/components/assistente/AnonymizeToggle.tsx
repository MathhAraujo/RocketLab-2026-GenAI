import type { JSX } from 'react';

type AnonymizeToggleProps = {
  checked: boolean;
  onChange: (value: boolean) => void;
};

export default function AnonymizeToggle({ checked, onChange }: AnonymizeToggleProps): JSX.Element {
  return (
    <div className="flex items-center gap-2">
      <span aria-hidden="true">🔒</span>
      <label
        htmlFor="anonimizar"
        className="cursor-pointer select-none text-sm text-gray-600 dark:text-gray-300"
      >
        Modo anônimo
      </label>
      <button
        id="anonimizar"
        type="button"
        role="switch"
        aria-checked={checked}
        aria-label="Modo anônimo"
        onClick={() => onChange(!checked)}
        className={[
          'relative inline-flex h-5 w-9 shrink-0 cursor-pointer rounded-full border-2 border-transparent',
          'transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-indigo-400 focus:ring-offset-1',
          checked ? 'bg-indigo-500 dark:bg-indigo-400' : 'bg-gray-300 dark:bg-gray-600',
        ].join(' ')}
      >
        <span
          aria-hidden="true"
          className={[
            'inline-block h-4 w-4 rounded-full bg-white shadow transition-transform duration-200',
            checked ? 'translate-x-4' : 'translate-x-0',
          ].join(' ')}
        />
      </button>
    </div>
  );
}
