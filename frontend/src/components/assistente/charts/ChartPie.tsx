import { Cell, Legend, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts';

const PIE_COLORS = ['#6366f1', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981', '#3b82f6'];
const CHART_HEIGHT = 320;

type ChartPieProps = {
  dados: Record<string, unknown>[];
  eixo_x: string;
  eixo_y: string;
};

export function ChartPie({ dados, eixo_x, eixo_y }: ChartPieProps): JSX.Element {
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
        <Tooltip />
        <Legend />
      </PieChart>
    </ResponsiveContainer>
  );
}
