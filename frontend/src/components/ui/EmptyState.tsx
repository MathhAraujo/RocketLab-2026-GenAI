import { PackageSearch } from 'lucide-react';

interface EmptyStateProps {
  title?: string;
  description?: string;
}

export function EmptyState({
  title = 'Nenhum resultado encontrado',
  description = 'Tente ajustar os filtros ou realizar uma nova busca.',
}: Readonly<EmptyStateProps>): JSX.Element {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-16 text-slate-400">
      <PackageSearch size={48} strokeWidth={1} className="text-slate-600" />
      <p className="text-base font-medium text-slate-300">{title}</p>
      <p className="text-sm">{description}</p>
    </div>
  );
}
