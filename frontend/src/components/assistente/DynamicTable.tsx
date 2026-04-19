import type { TabelaVisualizacao } from '../../types/assistente';

type DynamicTableProps = {
  visualizacao: TabelaVisualizacao;
};

function cellText(value: unknown): string {
  if (value == null) return '—';
  return String(value);
}

export function DynamicTable({ visualizacao }: DynamicTableProps): JSX.Element {
  const { titulo, colunas, linhas } = visualizacao;

  return (
    <div className="flex flex-col gap-2">
      {titulo && (
        <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-200">{titulo}</h3>
      )}
      <div className="overflow-x-auto rounded-lg border border-gray-200 dark:border-gray-700">
        <table className="min-w-full divide-y divide-gray-200 text-sm dark:divide-gray-700">
          <thead className="bg-gray-50 dark:bg-gray-800">
            <tr>
              {colunas.map((col) => (
                <th
                  key={col}
                  scope="col"
                  className="px-4 py-2 text-left font-medium text-gray-600 dark:text-gray-300"
                >
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100 bg-white dark:divide-gray-800 dark:bg-gray-900">
            {linhas.map((row, rowIdx) => (
              <tr key={`row-${rowIdx}`} className="hover:bg-gray-50 dark:hover:bg-gray-800/60">
                {row.map((cell, colIdx) => (
                  <td
                    key={`cell-${rowIdx}-${colIdx}`}
                    className="px-4 py-2 text-gray-700 dark:text-gray-300"
                  >
                    {cellText(cell)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {/* Export CSV button — TASK-29 */}
    </div>
  );
}
