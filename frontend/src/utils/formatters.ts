import type { FormatType } from '../types/assistente';
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
    .map((word) =>
      word === word.toUpperCase()
        ? word.toUpperCase()
        : word.charAt(0).toUpperCase() + word.slice(1).toLowerCase(),
    )
    .join(' ');
  if (titleCase.length <= maxLength) return titleCase;
  return `${titleCase.slice(0, maxLength)}…`;
}

function _formatFloatFixed(value: number): string {
  return value.toLocaleString('pt-BR', {
    minimumFractionDigits: MAX_DECIMAL_PLACES,
    maximumFractionDigits: MAX_DECIMAL_PLACES,
  });
}

export function formatCell(columnName: string, value: unknown, hint?: FormatType): string {
  if (value === null || value === undefined) return '—';
  if (typeof value !== 'number') return String(value);

  if (hint === 'monetario') return formatCurrency(value);
  if (hint === 'float') return _formatFloatFixed(value);
  if (hint === 'inteiro') return value.toLocaleString('pt-BR');
  if (hint === 'texto') return String(value);

  // Keyword fallback when no LLM hint is available.
  const lower = columnName.toLowerCase();
  if (MONETARY_KEYWORDS.some((kw) => lower.includes(kw))) {
    return formatCurrency(value);
  }
  if (Number.isInteger(value)) {
    return value.toLocaleString('pt-BR');
  }
  return value.toLocaleString('pt-BR', { maximumFractionDigits: MAX_DECIMAL_PLACES });
}
