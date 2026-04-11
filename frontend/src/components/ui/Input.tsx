import { type InputHTMLAttributes } from "react";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export function Input({ label, error, id, className = "", ...props }: Readonly<InputProps>) {
  return (
    <div className="flex flex-col gap-1.5">
      {label && (
        <label htmlFor={id} className="text-sm font-medium" style={{ color: "var(--color-text-secondary)" }}>
          {label}
        </label>
      )}
      <input
        id={id}
        className={`rounded-lg border px-3 py-2 text-sm transition-colors
          focus:outline-none focus:ring-2 focus:ring-indigo-500/40 focus:border-indigo-500
          disabled:cursor-not-allowed disabled:opacity-50
          ${error ? "border-rose-500" : ""}
          ${className}`}
        style={{
          background: "var(--color-bg-elevated)",
          borderColor: error ? undefined : "var(--color-border)",
          color: "var(--color-text-primary)",
        }}
        {...props}
      />
      {error && <p className="text-xs text-rose-400">{error}</p>}
    </div>
  );
}
