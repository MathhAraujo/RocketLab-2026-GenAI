import { CATEGORIA_LABELS } from './constants';

const MONETARY_KEYWORDS: readonly string[] = [
  'preco',
  'frete',
  'receita',
  'valor',
  'brl',
  'ticket',
];
const MAX_DECIMAL_PLACES = 4;
const MAX_LABEL_LENGTH = 12;

export function formatCategoria(slug: string | null | undefined): string {
  if (!slug) return 'Sem Categoria';
  return CATEGORIA_LABELS[slug] ?? slug.replace(/_/g, ' ');
}

export function formatCurrency(value: number | null | undefined): string {
  if (value == null) return '—';
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
  }).format(value);
}

export function formatDate(value: string | null | undefined): string {
  if (!value) return '—';
  return new Intl.DateTimeFormat('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  }).format(new Date(value));
}

export function formatNumber(value: number | null | undefined): string {
  if (value == null) return '—';
  return new Intl.NumberFormat('pt-BR').format(value);
}

export function formatRating(value: number | null | undefined): string {
  if (value == null) return '—';
  return value.toFixed(1);
}

export function sanitizeLabel(raw: string, maxLength: number = MAX_LABEL_LENGTH): string {
  const withoutParens = raw.replace(/\(.*$/, '');
  const withSpaces = withoutParens.replace(/_/g, ' ');
  const titleCase = withSpaces
    .split(' ')
    .filter(Boolean)
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ');
  if (titleCase.length <= maxLength) return titleCase;
  return `${titleCase.slice(0, maxLength)}…`;
}

export function formatCell(columnName: string, value: unknown): string {
  if (value === null || value === undefined) return '—';
  if (typeof value !== 'number') return String(value);

  const lower = columnName.toLowerCase();
  if (MONETARY_KEYWORDS.some((kw) => lower.includes(kw))) {
    return formatCurrency(value);
  }

  if (Number.isInteger(value)) {
    return value.toLocaleString('pt-BR');
  }

  return value.toLocaleString('pt-BR', { maximumFractionDigits: MAX_DECIMAL_PLACES });
}
