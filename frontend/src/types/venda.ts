export interface VendaStats {
  total_vendas: number;
  receita_total: number;
  preco_medio: number | null;
  preco_minimo: number | null;
  preco_maximo: number | null;
  total_pedidos: number;
  vendas_por_status: Record<string, number>;
}
