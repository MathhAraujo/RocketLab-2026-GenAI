import { CATEGORIA_LABELS } from "./constants";

export function formatCategoria(slug: string | null | undefined): string {
  if (!slug) return "—";
  return CATEGORIA_LABELS[slug] ?? slug.replace(/_/g, " ");
}

export function formatCurrency(value: number | null | undefined): string {
  if (value == null) return "—";
  return new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
  }).format(value);
}

export function formatDate(value: string | null | undefined): string {
  if (!value) return "—";
  return new Intl.DateTimeFormat("pt-BR", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  }).format(new Date(value));
}

export function formatNumber(value: number | null | undefined): string {
  if (value == null) return "—";
  return new Intl.NumberFormat("pt-BR").format(value);
}

export function formatRating(value: number | null | undefined): string {
  if (value == null) return "—";
  return value.toFixed(1);
}
