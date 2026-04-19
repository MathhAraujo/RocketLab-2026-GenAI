import { Star } from 'lucide-react';

interface StarRatingProps {
  rating: number | null;
  size?: number;
  showValue?: boolean;
}

export function StarRating({
  rating,
  size = 16,
  showValue = false,
}: Readonly<StarRatingProps>): JSX.Element {
  if (rating == null) {
    return <span className="text-slate-500 text-sm">Sem avaliações</span>;
  }

  return (
    <div className="flex items-center gap-1">
      {Array.from({ length: 5 }, (_, i) => {
        const fill = Math.min(1, Math.max(0, rating - i));
        return (
          <span key={i} className="relative inline-block" style={{ width: size, height: size }}>
            <Star size={size} className="text-slate-600" fill="none" strokeWidth={1.5} />
            {fill > 0 && (
              <span
                className="absolute inset-0 overflow-hidden"
                style={{ width: `${fill * 100}%` }}
              >
                <Star
                  size={size}
                  className="text-yellow-400"
                  fill="currentColor"
                  strokeWidth={1.5}
                />
              </span>
            )}
          </span>
        );
      })}
      {showValue && <span className="text-sm text-slate-400 ml-1">{rating.toFixed(1)}</span>}
    </div>
  );
}
