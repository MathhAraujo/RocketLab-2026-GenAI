export interface ProdutoListItem {
  id_produto: string;
  nome_produto: string;
  categoria_produto: string;
  preco_medio: number | null;
  avaliacao_media: number | null;
  total_avaliacoes: number;
  total_vendas: number;
}

export interface Produto {
  id_produto: string;
  nome_produto: string;
  categoria_produto: string;
  peso_produto_gramas: number | null;
  comprimento_centimetros: number | null;
  altura_centimetros: number | null;
  largura_centimetros: number | null;
  preco_medio: number | null;
  avaliacao_media: number | null;
  total_avaliacoes: number;
  total_vendas: number;
}

export interface ProdutoCreate {
  nome_produto: string;
  categoria_produto: string;
  peso_produto_gramas?: number | null;
  comprimento_centimetros?: number | null;
  altura_centimetros?: number | null;
  largura_centimetros?: number | null;
}

export interface ProdutoUpdate {
  nome_produto?: string;
  categoria_produto?: string;
  peso_produto_gramas?: number | null;
  comprimento_centimetros?: number | null;
  altura_centimetros?: number | null;
  largura_centimetros?: number | null;
}
