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
import { formatCell, sanitizeLabel } from '../../../utils/formatters';

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
  const tooltipBg = isDark ? '#1f2937' : '#ffffff';
  const tooltipBorder = isDark ? '#374151' : '#e5e7eb';
  const tooltipTitle = isDark ? '#f3f4f6' : '#111827';
  const tooltipText = isDark ? '#9ca3af' : '#6b7280';

  return (
    <ResponsiveContainer width="100%" height={CHART_HEIGHT}>
      <LineChart data={dados} margin={{ top: 8, right: 16, bottom: 72, left: 60 }}>
        <CartesianGrid strokeDasharray="3 3" stroke={gridColor} />
        <XAxis
          dataKey={eixo_x}
          stroke={axisColor}
          angle={-45}
          textAnchor="end"
          interval={0}
          tickFormatter={(v: unknown) => sanitizeLabel(String(v))}
        />
        <YAxis stroke={axisColor} />
        <Tooltip
          content={(props) => {
            if (!props.active || !props.payload?.length) return null;
            const item = props.payload[0];
            if (!item) return null;
            const category = (item.payload as Record<string, unknown>)[eixo_x];
            return (
              <div
                style={{
                  background: tooltipBg,
                  border: `1px solid ${tooltipBorder}`,
                  borderRadius: 6,
                  padding: '6px 10px',
                  fontSize: 12,
                }}
              >
                <p style={{ color: tooltipTitle, fontWeight: 600, marginBottom: 2 }}>
                  {sanitizeLabel(String(category ?? ''), Infinity)}
                </p>
                <p style={{ color: tooltipText }}>
                  {sanitizeLabel(String(item.name))}: {formatCell(eixo_y, item.value)}
                </p>
              </div>
            );
          }}
        />
        <Line type="monotone" dataKey={eixo_y} stroke={chartColor} dot={false} strokeWidth={2} />
      </LineChart>
    </ResponsiveContainer>
  );
}
