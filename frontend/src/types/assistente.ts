type ChartSubtipo = 'bar' | 'line' | 'pie' | 'area' | 'scatter';

type PerguntaRequest = {
  pergunta: string;
  anonimizar: boolean;
};

type TabelaVisualizacao = {
  tipo: 'tabela';
  titulo: string;
  colunas: string[];
  linhas: unknown[][];
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
  metadados: MetadadosResposta;
};

export type {
  ChartSubtipo,
  GraficoVisualizacao,
  MetadadosResposta,
  PerguntaRequest,
  RespostaAssistente,
  TabelaVisualizacao,
  Visualizacao,
};
