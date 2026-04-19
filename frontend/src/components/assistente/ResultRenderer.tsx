import type { Visualizacao } from '../../types/assistente';
import { DynamicChart } from './DynamicChart';
import { DynamicTable } from './DynamicTable';

type ResultRendererProps = {
  visualizacoes: Visualizacao[];
};

export function ResultRenderer({ visualizacoes }: ResultRendererProps): JSX.Element {
  return (
    <div className="flex flex-col gap-6">
      {visualizacoes.map((v, idx) =>
        v.tipo === 'tabela' ? (
          <DynamicTable key={`viz-${idx}`} visualizacao={v} />
        ) : (
          <DynamicChart key={`viz-${idx}`} visualizacao={v} />
        ),
      )}
    </div>
  );
}
