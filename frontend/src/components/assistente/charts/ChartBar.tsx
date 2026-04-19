import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';

const CHART_COLOR = '#6366f1';
const AXIS_COLOR = '#9ca3af';
const GRID_COLOR = '#e5e7eb';
const CHART_HEIGHT = 300;

type ChartBarProps = {
  dados: Record<string, unknown>[];
  eixo_x: string;
  eixo_y: string;
};

export function ChartBar({ dados, eixo_x, eixo_y }: ChartBarProps): JSX.Element {
  return (
    <ResponsiveContainer width="100%" height={CHART_HEIGHT}>
      <BarChart data={dados} margin={{ top: 8, right: 16, bottom: 48, left: 16 }}>
        <CartesianGrid strokeDasharray="3 3" stroke={GRID_COLOR} />
        <XAxis dataKey={eixo_x} stroke={AXIS_COLOR} angle={-30} textAnchor="end" interval={0} />
        <YAxis stroke={AXIS_COLOR} />
        <Tooltip />
        <Bar dataKey={eixo_y} fill={CHART_COLOR} radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}
