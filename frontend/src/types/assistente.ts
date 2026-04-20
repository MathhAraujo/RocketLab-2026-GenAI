type ChartSubtipo = 'bar' | 'line' | 'pie' | 'area' | 'scatter';

type FormatType = 'monetario' | 'float' | 'inteiro' | 'texto';

type PerguntaRequest = {
  pergunta: string;
  anonimizar: boolean;
};

type TabelaVisualizacao = {
  tipo: 'tabela';
  titulo: string;
  colunas: string[];
  linhas: unknown[][];
  formatacao_colunas: Record<string, FormatType> | null;
};

type GraficoVisualizacao = {
  tipo: 'grafico';
  subtipo: ChartSubtipo;
  titulo: string;
  eixo_x: string;
  eixo_y: string;
  dados: Record<string, unknown>[];
};

type Visualizacao = TabelaVisualizacao | GraficoVisualizacao;

type MetadadosResposta = {
  anonimizado: boolean;
  linhas_retornadas: number;
  usou_insight: boolean;
  motivo: string | null;
};

type RespostaAssistente = {
  pergunta: string;
  sql_gerado: string | null;
  explicacao: string | null;
  visualizacoes: Visualizacao[];
  tentativas: number;
  erro_amigavel: string | null;
  traducao_anonimizacao: Record<string, string> | null;
  metadados: MetadadosResposta;
};

export type {
  ChartSubtipo,
  FormatType,
  GraficoVisualizacao,
  MetadadosResposta,
  PerguntaRequest,
  RespostaAssistente,
  TabelaVisualizacao,
  Visualizacao,
};
