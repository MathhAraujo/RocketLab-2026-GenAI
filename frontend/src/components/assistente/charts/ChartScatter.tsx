import {
  CartesianGrid,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

import { useTheme } from '../../../contexts/ThemeContext';
import { formatCell, sanitizeLabel } from '../../../utils/formatters';

const CHART_HEIGHT = 300;

type ChartScatterProps = {
  dados: Record<string, unknown>[];
  eixo_x: string;
  eixo_y: string;
};

export function ChartScatter({ dados, eixo_x, eixo_y }: ChartScatterProps): JSX.Element {
  const { theme } = useTheme();
  const isDark = theme === 'dark';

  const gridColor = isDark ? '#3f3f46' : '#e5e7eb';
  const axisColor = isDark ? '#71717a' : '#9ca3af';
  const chartColor = isDark ? '#818cf8' : '#6366f1';

  const points = dados.map((row) => ({ x: Number(row[eixo_x]), y: Number(row[eixo_y]) }));

  return (
    <ResponsiveContainer width="100%" height={CHART_HEIGHT}>
      <ScatterChart margin={{ top: 8, right: 16, bottom: 8, left: 16 }}>
        <CartesianGrid stroke={gridColor} />
        <XAxis dataKey="x" name={eixo_x} stroke={axisColor} type="number" />
        <YAxis dataKey="y" name={eixo_y} stroke={axisColor} type="number" />
        <Tooltip
          cursor={{ strokeDasharray: '3 3' }}
          formatter={(value, name) => [
            formatCell(String(name), value),
            sanitizeLabel(String(name)),
          ]}
        />
        <Scatter data={points} fill={chartColor} />
      </ScatterChart>
    </ResponsiveContainer>
  );
}
