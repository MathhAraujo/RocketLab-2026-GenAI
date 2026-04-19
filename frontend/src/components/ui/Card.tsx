import { type ReactNode } from 'react';

interface CardProps {
  children: ReactNode;
  className?: string;
  onClick?: () => void;
}

export function Card({ children, className = '', onClick }: Readonly<CardProps>): JSX.Element {
  return (
    <div
      onClick={onClick}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
      onKeyDown={onClick ? (e) => e.key === 'Enter' && onClick() : undefined}
      style={{ background: 'var(--color-bg-surface)', borderColor: 'var(--color-border)' }}
      className={`rounded-xl border shadow-sm
        ${
          onClick
            ? 'cursor-pointer hover:border-indigo-500/40 hover:shadow-lg hover:shadow-indigo-950/30 hover:-translate-y-0.5 transition-all duration-200'
            : ''
        }
        ${className}`}
    >
      {children}
    </div>
  );
}
