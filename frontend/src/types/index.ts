export interface Produto {
  id_produto: string
  nome_produto: string
  categoria_produto: string
  peso_produto_gramas: number | null
  comprimento_centimetros: number | null
  altura_centimetros: number | null
  largura_centimetros: number | null
}

export interface AvaliacaoResumo {
  total_avaliacoes: number
  media_avaliacao: number
}

export interface VendaResumo {
  total_vendas: number
  receita_total: number
}

export interface ProdutoDetalhes extends Produto {
  avaliacoes: AvaliacaoResumo
  vendas: VendaResumo
}

export interface ProdutoCreate {
  nome_produto: string
  categoria_produto: string
  peso_produto_gramas?: number | null
  comprimento_centimetros?: number | null
  altura_centimetros?: number | null
  largura_centimetros?: number | null
}

export type ProdutoUpdate = Partial<ProdutoCreate>
