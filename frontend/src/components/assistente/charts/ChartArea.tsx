import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

import { useTheme } from '../../../contexts/ThemeContext';

const CHART_HEIGHT = 300;

type ChartAreaProps = {
  dados: Record<string, unknown>[];
  eixo_x: string;
  eixo_y: string;
};

export function ChartArea({ dados, eixo_x, eixo_y }: ChartAreaProps): JSX.Element {
  const { theme } = useTheme();
  const isDark = theme === 'dark';

  const gridColor = isDark ? '#3f3f46' : '#e5e7eb';
  const axisColor = isDark ? '#71717a' : '#9ca3af';
  const chartColor = isDark ? '#818cf8' : '#6366f1';
  const chartColorFill = isDark ? '#818cf833' : '#6366f133';

  return (
    <ResponsiveContainer width="100%" height={CHART_HEIGHT}>
      <AreaChart data={dados} margin={{ top: 8, right: 16, bottom: 48, left: 16 }}>
        <CartesianGrid strokeDasharray="3 3" stroke={gridColor} />
        <XAxis dataKey={eixo_x} stroke={axisColor} angle={-30} textAnchor="end" interval={0} />
        <YAxis stroke={axisColor} />
        <Tooltip />
        <Area
          type="monotone"
          dataKey={eixo_y}
          stroke={chartColor}
          fill={chartColorFill}
          strokeWidth={2}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}
