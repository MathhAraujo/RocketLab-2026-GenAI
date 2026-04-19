import { Cell, Legend, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts';

import { useTheme } from '../../../contexts/ThemeContext';
import { formatCell, sanitizeLabel } from '../../../utils/formatters';

const PIE_COLORS = ['#6366f1', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981', '#3b82f6'];
const CHART_HEIGHT = 320;

type ChartPieProps = {
  dados: Record<string, unknown>[];
  eixo_x: string;
  eixo_y: string;
};

export function ChartPie({ dados, eixo_x, eixo_y }: ChartPieProps): JSX.Element {
  const { theme } = useTheme();
  const isDark = theme === 'dark';

  const legendTextColor = isDark ? '#d4d4d8' : '#3f3f46';

  return (
    <ResponsiveContainer width="100%" height={CHART_HEIGHT}>
      <PieChart>
        <Pie
          data={dados}
          dataKey={eixo_y}
          nameKey={eixo_x}
          cx="50%"
          cy="45%"
          outerRadius={110}
          label={false}
        >
          {dados.map((_, idx) => (
            <Cell key={`slice-${idx}`} fill={PIE_COLORS[idx % PIE_COLORS.length]} />
          ))}
        </Pie>
        <Tooltip
          formatter={(value, name) => [formatCell(eixo_y, value), sanitizeLabel(String(name))]}
        />
        <Legend
          wrapperStyle={{ color: legendTextColor }}
          formatter={(value) => sanitizeLabel(String(value))}
        />
      </PieChart>
    </ResponsiveContainer>
  );
}
