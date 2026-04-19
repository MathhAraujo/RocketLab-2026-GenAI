import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';

import { useTheme } from '../../../contexts/ThemeContext';
import { formatCell, sanitizeLabel } from '../../../utils/formatters';

const CHART_HEIGHT = 300;

type ChartBarProps = {
  dados: Record<string, unknown>[];
  eixo_x: string;
  eixo_y: string;
};

export function ChartBar({ dados, eixo_x, eixo_y }: ChartBarProps): JSX.Element {
  const { theme } = useTheme();
  const isDark = theme === 'dark';

  const gridColor = isDark ? '#3f3f46' : '#e5e7eb';
  const axisColor = isDark ? '#71717a' : '#9ca3af';
  const chartColor = isDark ? '#818cf8' : '#6366f1';

  return (
    <ResponsiveContainer width="100%" height={CHART_HEIGHT}>
      <BarChart data={dados} margin={{ top: 8, right: 16, bottom: 48, left: 16 }}>
        <CartesianGrid strokeDasharray="3 3" stroke={gridColor} />
        <XAxis
          dataKey={eixo_x}
          stroke={axisColor}
          angle={-30}
          textAnchor="end"
          interval={0}
          tickFormatter={(v: unknown) => sanitizeLabel(String(v))}
        />
        <YAxis stroke={axisColor} />
        <Tooltip
          formatter={(value, name) => [formatCell(eixo_y, value), sanitizeLabel(String(name))]}
        />
        <Bar dataKey={eixo_y} fill={chartColor} radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}
