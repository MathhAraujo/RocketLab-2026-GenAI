import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

const CHART_COLOR = '#6366f1';
const AXIS_COLOR = '#9ca3af';
const GRID_COLOR = '#e5e7eb';
const CHART_HEIGHT = 300;

type ChartLineProps = {
  dados: Record<string, unknown>[];
  eixo_x: string;
  eixo_y: string;
};

export function ChartLine({ dados, eixo_x, eixo_y }: ChartLineProps): JSX.Element {
  return (
    <ResponsiveContainer width="100%" height={CHART_HEIGHT}>
      <LineChart data={dados} margin={{ top: 8, right: 16, bottom: 48, left: 16 }}>
        <CartesianGrid strokeDasharray="3 3" stroke={GRID_COLOR} />
        <XAxis dataKey={eixo_x} stroke={AXIS_COLOR} angle={-30} textAnchor="end" interval={0} />
        <YAxis stroke={AXIS_COLOR} />
        <Tooltip />
        <Line type="monotone" dataKey={eixo_y} stroke={CHART_COLOR} dot={false} strokeWidth={2} />
      </LineChart>
    </ResponsiveContainer>
  );
}
