import { type LucideIcon } from 'lucide-react';

interface StatCardProps {
  icon: LucideIcon;
  label: string;
  value: string;
  iconColor?: string;
}

export function StatCard({
  icon: Icon,
  label,
  value,
  iconColor = 'text-zinc-400',
}: Readonly<StatCardProps>): JSX.Element {
  return (
    <div
      className="rounded-xl border p-4 flex flex-col gap-2"
      style={{
        background: 'var(--color-bg-surface)',
        borderColor: 'var(--color-border)',
      }}
    >
      <Icon size={18} className={iconColor} />
      <p
        className="text-xs uppercase tracking-wide font-medium"
        style={{ color: 'var(--color-text-secondary)' }}
      >
        {label}
      </p>
      <p
        className="text-2xl font-bold leading-none"
        style={{ fontFamily: "'Outfit', sans-serif", color: 'var(--color-text-primary)' }}
      >
        {value}
      </p>
    </div>
  );
}
