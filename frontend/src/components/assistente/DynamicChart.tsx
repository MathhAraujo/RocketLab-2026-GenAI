import html2canvas from 'html2canvas';
import { useRef } from 'react';

import type { GraficoVisualizacao } from '../../types/assistente';
import { ChartArea } from './charts/ChartArea';
import { ChartBar } from './charts/ChartBar';
import { ChartLine } from './charts/ChartLine';
import { ChartPie } from './charts/ChartPie';
import { ChartScatter } from './charts/ChartScatter';

const FALLBACK_SLUG = 'grafico';

type DynamicChartProps = {
  visualizacao: GraficoVisualizacao;
  isAdmin: boolean;
};

function toSlug(text: string): string {
  return text
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
}

export function DynamicChart({ visualizacao, isAdmin }: DynamicChartProps): JSX.Element {
  const { subtipo, titulo, eixo_x, eixo_y, dados } = visualizacao;
  const props = { dados, eixo_x, eixo_y };
  const containerRef = useRef<HTMLDivElement>(null);

  const handleDownloadPng = async () => {
    if (!containerRef.current) return;
    const canvas = await html2canvas(containerRef.current, { useCORS: true });
    canvas.toBlob((blob) => {
      if (!blob) return;
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement('a');
      anchor.href = url;
      anchor.download = `${toSlug(titulo) || FALLBACK_SLUG}-${Date.now()}.png`;
      anchor.click();
      URL.revokeObjectURL(url);
    });
  };

  return (
    <div className="flex flex-col gap-2">
      <div className="flex items-center justify-between">
        {titulo && (
          <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-200">{titulo}</h3>
        )}
        {isAdmin && (
          <button
            type="button"
            onClick={() => void handleDownloadPng()}
            className="ml-auto rounded px-2 py-1 text-xs text-blue-600 hover:bg-blue-50 dark:text-blue-400 dark:hover:bg-blue-950"
            aria-label="Baixar gráfico como PNG"
          >
            ⬇ PNG
          </button>
        )}
      </div>
      <div ref={containerRef} className="w-full">
        {subtipo === 'bar' && <ChartBar {...props} />}
        {subtipo === 'line' && <ChartLine {...props} />}
        {subtipo === 'pie' && <ChartPie {...props} />}
        {subtipo === 'area' && <ChartArea {...props} />}
        {subtipo === 'scatter' && <ChartScatter {...props} />}
      </div>
    </div>
  );
}
