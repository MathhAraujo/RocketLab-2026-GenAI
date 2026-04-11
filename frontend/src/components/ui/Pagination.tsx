import { ChevronLeft, ChevronRight } from "lucide-react";

interface PaginationProps {
  page: number;
  pages: number;
  total: number;
  perPage: number;
  onPageChange: (page: number) => void;
}

export function Pagination({
  page,
  pages,
  total,
  perPage,
  onPageChange,
}: Readonly<PaginationProps>) {
  if (pages <= 1) return null;

  const from = (page - 1) * perPage + 1;
  const to = Math.min(page * perPage, total);

  return (
    <div className="flex items-center justify-between text-sm text-slate-400">
      <span>
        {from}–{to} de {total}
      </span>
      <div className="flex items-center gap-1">
        <button
          onClick={() => onPageChange(page - 1)}
          disabled={page <= 1}
          className="rounded p-1 hover:bg-slate-700 disabled:cursor-not-allowed disabled:opacity-40"
          aria-label="Página anterior"
        >
          <ChevronLeft size={18} />
        </button>
        {Array.from({ length: Math.min(pages, 7) }, (_, i) => {
          const p = i + 1;
          return (
            <button
              key={p}
              onClick={() => onPageChange(p)}
              className={`rounded px-2 py-1 ${
                p === page
                  ? "bg-violet-600 text-white"
                  : "hover:bg-slate-700 text-slate-300"
              }`}
            >
              {p}
            </button>
          );
        })}
        {pages > 7 && page < pages - 3 && (
          <>
            <span>…</span>
            <button
              onClick={() => onPageChange(pages)}
              className="rounded px-2 py-1 hover:bg-slate-700 text-slate-300"
            >
              {pages}
            </button>
          </>
        )}
        <button
          onClick={() => onPageChange(page + 1)}
          disabled={page >= pages}
          className="rounded p-1 hover:bg-slate-700 disabled:cursor-not-allowed disabled:opacity-40"
          aria-label="Próxima página"
        >
          <ChevronRight size={18} />
        </button>
      </div>
    </div>
  );
}
