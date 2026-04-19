import { ChevronDown } from 'lucide-react';
import { type SelectHTMLAttributes } from 'react';

interface Option {
  value: string;
  label: string;
}

interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  options: Option[];
  placeholder?: string;
}

export function Select({
  label,
  options,
  placeholder,
  id,
  className = '',
  ...props
}: Readonly<SelectProps>): JSX.Element {
  return (
    <div className="flex flex-col gap-1.5">
      {label && (
        <label
          htmlFor={id}
          className="text-sm font-medium"
          style={{ color: 'var(--color-text-secondary)' }}
        >
          {label}
        </label>
      )}
      <div className="relative">
        <select
          id={id}
          className={`w-full appearance-none rounded-lg border px-3 py-2 pr-8 text-sm
            transition-colors focus:outline-none focus:ring-2 focus:ring-indigo-500/40
            focus:border-indigo-500 ${className}`}
          style={{
            background: 'var(--color-bg-elevated)',
            borderColor: 'var(--color-border)',
            color: 'var(--color-text-primary)',
          }}
          {...props}
        >
          {placeholder && <option value="">{placeholder}</option>}
          {options.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
        <ChevronDown
          size={14}
          className="pointer-events-none absolute right-2.5 top-1/2 -translate-y-1/2"
          style={{ color: 'var(--color-text-muted)' }}
        />
      </div>
    </div>
  );
}
