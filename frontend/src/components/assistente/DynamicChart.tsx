import type { GraficoVisualizacao } from '../../types/assistente';
import { ChartArea } from './charts/ChartArea';
import { ChartBar } from './charts/ChartBar';
import { ChartLine } from './charts/ChartLine';
import { ChartPie } from './charts/ChartPie';
import { ChartScatter } from './charts/ChartScatter';

type DynamicChartProps = {
  visualizacao: GraficoVisualizacao;
};

export function DynamicChart({ visualizacao }: DynamicChartProps): JSX.Element {
  const { subtipo, titulo, eixo_x, eixo_y, dados } = visualizacao;
  const props = { dados, eixo_x, eixo_y };

  return (
    <div className="flex flex-col gap-2">
      {titulo && (
        <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-200">{titulo}</h3>
      )}
      <div className="w-full">
        {subtipo === 'bar' && <ChartBar {...props} />}
        {subtipo === 'line' && <ChartLine {...props} />}
        {subtipo === 'pie' && <ChartPie {...props} />}
        {subtipo === 'area' && <ChartArea {...props} />}
        {subtipo === 'scatter' && <ChartScatter {...props} />}
      </div>
      {/* Export PNG button — TASK-30 */}
    </div>
  );
}
