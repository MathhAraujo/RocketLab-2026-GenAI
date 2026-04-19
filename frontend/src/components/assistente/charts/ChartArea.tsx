import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

const CHART_COLOR = '#6366f1';
const CHART_COLOR_FILL = '#6366f133';
const AXIS_COLOR = '#9ca3af';
const GRID_COLOR = '#e5e7eb';
const CHART_HEIGHT = 300;

type ChartAreaProps = {
  dados: Record<string, unknown>[];
  eixo_x: string;
  eixo_y: string;
};

export function ChartArea({ dados, eixo_x, eixo_y }: ChartAreaProps): JSX.Element {
  return (
    <ResponsiveContainer width="100%" height={CHART_HEIGHT}>
      <AreaChart data={dados} margin={{ top: 8, right: 16, bottom: 48, left: 16 }}>
        <CartesianGrid strokeDasharray="3 3" stroke={GRID_COLOR} />
        <XAxis dataKey={eixo_x} stroke={AXIS_COLOR} angle={-30} textAnchor="end" interval={0} />
        <YAxis stroke={AXIS_COLOR} />
        <Tooltip />
        <Area
          type="monotone"
          dataKey={eixo_y}
          stroke={CHART_COLOR}
          fill={CHART_COLOR_FILL}
          strokeWidth={2}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}
