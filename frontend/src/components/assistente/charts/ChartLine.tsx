import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

import { useTheme } from '../../../contexts/ThemeContext';

const CHART_HEIGHT = 300;

type ChartLineProps = {
  dados: Record<string, unknown>[];
  eixo_x: string;
  eixo_y: string;
};

export function ChartLine({ dados, eixo_x, eixo_y }: ChartLineProps): JSX.Element {
  const { theme } = useTheme();
  const isDark = theme === 'dark';

  const gridColor = isDark ? '#3f3f46' : '#e5e7eb';
  const axisColor = isDark ? '#71717a' : '#9ca3af';
  const chartColor = isDark ? '#818cf8' : '#6366f1';

  return (
    <ResponsiveContainer width="100%" height={CHART_HEIGHT}>
      <LineChart data={dados} margin={{ top: 8, right: 16, bottom: 48, left: 16 }}>
        <CartesianGrid strokeDasharray="3 3" stroke={gridColor} />
        <XAxis dataKey={eixo_x} stroke={axisColor} angle={-30} textAnchor="end" interval={0} />
        <YAxis stroke={axisColor} />
        <Tooltip />
        <Line type="monotone" dataKey={eixo_y} stroke={chartColor} dot={false} strokeWidth={2} />
      </LineChart>
    </ResponsiveContainer>
  );
}
