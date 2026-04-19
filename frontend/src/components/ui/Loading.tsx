interface LoadingProps {
  message?: string;
}

export function Loading({ message = 'Carregando...' }: Readonly<LoadingProps>): JSX.Element {
  return (
    <div
      className="flex flex-col items-center justify-center gap-3 py-16"
      style={{ color: 'var(--color-text-secondary)' }}
    >
      <span
        className="size-8 animate-spin rounded-full border-2 border-t-indigo-500"
        style={{ borderColor: 'var(--color-border)', borderTopColor: '#6366f1' }}
      />
      <span className="text-sm">{message}</span>
    </div>
  );
}

export function SkeletonCard(): JSX.Element {
  return (
    <div
      className="rounded-xl border animate-pulse overflow-hidden"
      style={{ background: 'var(--color-bg-surface)', borderColor: 'var(--color-border)' }}
    >
      {/* image area */}
      <div className="h-44 w-full" style={{ background: 'var(--color-bg-elevated)' }} />
      <div className="p-4 space-y-3">
        {/* badge */}
        <div className="h-5 w-20 rounded-full" style={{ background: 'var(--color-bg-elevated)' }} />
        {/* title */}
        <div className="h-4 w-full rounded" style={{ background: 'var(--color-bg-elevated)' }} />
        <div className="h-4 w-3/4 rounded" style={{ background: 'var(--color-bg-elevated)' }} />
        {/* price row */}
        <div className="flex justify-between pt-1">
          <div className="h-5 w-24 rounded" style={{ background: 'var(--color-bg-elevated)' }} />
          <div className="h-4 w-16 rounded" style={{ background: 'var(--color-bg-elevated)' }} />
        </div>
      </div>
    </div>
  );
}
