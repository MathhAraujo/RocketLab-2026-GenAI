import {
  CartesianGrid,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

const CHART_COLOR = '#6366f1';
const AXIS_COLOR = '#9ca3af';
const GRID_COLOR = '#e5e7eb';
const CHART_HEIGHT = 300;

type ChartScatterProps = {
  dados: Record<string, unknown>[];
  eixo_x: string;
  eixo_y: string;
};

export function ChartScatter({ dados, eixo_x, eixo_y }: ChartScatterProps): JSX.Element {
  const points = dados.map((row) => ({ x: Number(row[eixo_x]), y: Number(row[eixo_y]) }));

  return (
    <ResponsiveContainer width="100%" height={CHART_HEIGHT}>
      <ScatterChart margin={{ top: 8, right: 16, bottom: 8, left: 16 }}>
        <CartesianGrid stroke={GRID_COLOR} />
        <XAxis dataKey="x" name={eixo_x} stroke={AXIS_COLOR} type="number" />
        <YAxis dataKey="y" name={eixo_y} stroke={AXIS_COLOR} type="number" />
        <Tooltip cursor={{ strokeDasharray: '3 3' }} />
        <Scatter data={points} fill={CHART_COLOR} />
      </ScatterChart>
    </ResponsiveContainer>
  );
}
