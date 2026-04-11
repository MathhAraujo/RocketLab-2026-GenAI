import { type ButtonHTMLAttributes } from "react";

type Variant = "primary" | "secondary" | "danger";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  isLoading?: boolean;
}

const variantClasses: Record<Variant, string> = {
  primary:
    "bg-indigo-500 hover:bg-indigo-400 text-white focus:ring-indigo-500",
  secondary:
    "bg-zinc-800 hover:bg-zinc-700 text-zinc-200 border border-zinc-700 focus:ring-zinc-500 dark:bg-zinc-800 dark:hover:bg-zinc-700 dark:border-zinc-700 not-dark:bg-zinc-100 not-dark:hover:bg-zinc-200 not-dark:text-zinc-800 not-dark:border-zinc-200",
  danger:
    "bg-rose-500 hover:bg-rose-400 text-white focus:ring-rose-500",
};

export function Button({
  variant = "primary",
  isLoading = false,
  disabled,
  children,
  className = "",
  ...props
}: Readonly<ButtonProps>) {
  return (
    <button
      disabled={disabled ?? isLoading}
      className={`inline-flex items-center justify-center gap-2 rounded-lg px-4 py-2 text-sm font-medium
        transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2
        focus:ring-offset-[var(--color-bg-base)]
        disabled:cursor-not-allowed disabled:opacity-50
        ${variantClasses[variant]} ${className}`}
      {...props}
    >
      {isLoading && (
        <span className="size-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
      )}
      {children}
    </button>
  );
}
