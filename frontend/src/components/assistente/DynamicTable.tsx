import type { TabelaVisualizacao } from '../../types/assistente';

const FALLBACK_SLUG = 'tabela';

type DynamicTableProps = {
  visualizacao: TabelaVisualizacao;
  isAdmin: boolean;
};

function cellText(value: unknown): string {
  if (value == null) return '—';
  return String(value);
}

function escapeCsvCell(value: unknown): string {
  const text = value == null ? '' : String(value);
  if (text.includes(',') || text.includes('"') || text.includes('\n')) {
    return `"${text.replace(/"/g, '""')}"`;
  }
  return text;
}

function buildCsv(colunas: string[], linhas: unknown[][]): string {
  const header = colunas.map(escapeCsvCell).join(',');
  const rows = linhas.map((row) => row.map(escapeCsvCell).join(','));
  return [header, ...rows].join('\n');
}

function toSlug(text: string): string {
  return text
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
}

function downloadCsv(content: string, filename: string): void {
  const blob = new Blob([content], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(url);
}

export function DynamicTable({ visualizacao, isAdmin }: DynamicTableProps): JSX.Element {
  const { titulo, colunas, linhas } = visualizacao;

  const handleDownloadCsv = () => {
    const slug = toSlug(titulo) || FALLBACK_SLUG;
    downloadCsv(buildCsv(colunas, linhas), `${slug}-${Date.now()}.csv`);
  };

  return (
    <div className="flex flex-col gap-2">
      <div className="flex items-center justify-between">
        {titulo && (
          <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-200">{titulo}</h3>
        )}
        {isAdmin && (
          <button
            type="button"
            onClick={handleDownloadCsv}
            className="ml-auto rounded px-2 py-1 text-xs text-blue-600 hover:bg-blue-50 dark:text-blue-400 dark:hover:bg-blue-950"
            aria-label="Baixar tabela como CSV"
          >
            ⬇ CSV
          </button>
        )}
      </div>
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
    </div>
  );
}
