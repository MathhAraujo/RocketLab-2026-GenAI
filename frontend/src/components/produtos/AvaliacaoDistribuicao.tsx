import { Star } from 'lucide-react';
import type { AvaliacaoStats } from '../../types/avaliacao';
import { formatNumber } from '../../utils/formatters';
import { StarRating } from '../ui/StarRating';

interface AvaliacaoDistribuicaoProps {
  stats: AvaliacaoStats;
}

export function AvaliacaoDistribuicao({
  stats,
}: Readonly<AvaliacaoDistribuicaoProps>): JSX.Element {
  const max = Math.max(...Object.values(stats.distribuicao), 1);

  return (
    <div className="flex flex-col gap-4 sm:flex-row sm:items-center">
      <div className="flex flex-col items-center gap-1 min-w-[100px]">
        <span className="text-4xl font-bold" style={{ color: 'var(--color-text-primary)' }}>
          {stats.avaliacao_media == null ? '—' : stats.avaliacao_media.toFixed(1)}
        </span>
        <StarRating rating={stats.avaliacao_media} size={18} />
        <span className="text-xs" style={{ color: 'var(--color-text-secondary)' }}>
          {formatNumber(stats.total_avaliacoes)} avaliações
        </span>
      </div>

      <div className="flex-1 space-y-1.5">
        {[5, 4, 3, 2, 1].map((star) => {
          const count = stats.distribuicao[star] ?? 0;
          const pct = max > 0 ? (count / max) * 100 : 0;
          return (
            <div key={star} className="flex items-center gap-2 text-xs">
              <span
                className="flex items-center gap-0.5 w-6 shrink-0"
                style={{ color: 'var(--color-text-secondary)' }}
              >
                {star}
                <Star size={10} className="text-yellow-400" fill="currentColor" />
              </span>
              <div
                className="flex-1 h-1.5 rounded-full overflow-hidden"
                style={{ background: 'var(--color-bg-elevated)' }}
              >
                <div
                  className="h-full rounded-full bg-yellow-400 transition-all"
                  style={{ width: `${pct}%` }}
                />
              </div>
              <span
                className="w-8 text-right shrink-0"
                style={{ color: 'var(--color-text-muted)' }}
              >
                {formatNumber(count)}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
