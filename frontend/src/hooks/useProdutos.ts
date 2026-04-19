import { useEffect, useState } from 'react';
import { getProdutos, type ProdutosParams } from '../api/produtos';
import type { PaginatedResponse } from '../types/pagination';
import type { ProdutoListItem } from '../types/produto';

export function useProdutos({
  page,
  per_page,
  search,
  categoria,
  sort_by,
  order,
}: ProdutosParams): {
  data: PaginatedResponse<ProdutoListItem> | null;
  isLoading: boolean;
  error: string | null;
} {
  const [data, setData] = useState<PaginatedResponse<ProdutoListItem> | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setIsLoading(true);
    setError(null);

    getProdutos({ page, per_page, search, categoria, sort_by, order })
      .then((res) => {
        if (!cancelled) {
          setData(res);
          setIsLoading(false);
        }
      })
      .catch(() => {
        if (!cancelled) {
          setError('Erro ao carregar produtos');
          setIsLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [page, per_page, search, categoria, sort_by, order]);

  return { data, isLoading, error };
}
