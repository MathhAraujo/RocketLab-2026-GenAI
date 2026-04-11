import type { AvaliacaoStats } from "../../types/avaliacao";
import { formatDate } from "../../utils/formatters";
import { Pagination } from "../ui/Pagination";
import { StarRating } from "../ui/StarRating";

interface AvaliacoesListProps {
  stats: AvaliacaoStats;
  onPageChange: (page: number) => void;
}

export function AvaliacoesList({ stats, onPageChange }: Readonly<AvaliacoesListProps>) {
  if (stats.avaliacoes.length === 0) {
    return (
      <p className="py-6 text-center text-sm" style={{ color: "var(--color-text-secondary)" }}>
        Nenhuma avaliação encontrada.
      </p>
    );
  }

  return (
    <div className="space-y-4">
      {stats.avaliacoes.map((av) => (
        <div
          key={av.id_avaliacao}
          className="rounded-xl border p-4"
          style={{
            background: "var(--color-bg-surface)",
            borderColor: "var(--color-border)",
          }}
        >
          <div className="mb-2 flex items-center justify-between">
            <StarRating rating={av.avaliacao} size={14} />
            <span className="text-xs" style={{ color: "var(--color-text-secondary)" }}>
              {formatDate(av.data_comentario)}
            </span>
          </div>
          {av.titulo_comentario && av.titulo_comentario !== "Sem titulo" && (
            <p
              className="mb-1 text-sm font-medium"
              style={{ color: "var(--color-text-primary)" }}
            >
              {av.titulo_comentario}
            </p>
          )}
          {av.comentario && av.comentario !== "Sem comentario" && (
            <p className="text-sm" style={{ color: "var(--color-text-secondary)" }}>
              {av.comentario}
            </p>
          )}
        </div>
      ))}

      <Pagination
        page={stats.page}
        pages={stats.pages}
        total={stats.total}
        perPage={stats.per_page}
        onPageChange={onPageChange}
      />
    </div>
  );
}
