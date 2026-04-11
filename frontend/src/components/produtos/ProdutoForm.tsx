import { useState } from "react";
import type { Produto, ProdutoCreate, ProdutoUpdate } from "../../types/produto";
import { Button } from "../ui/Button";
import { Input } from "../ui/Input";
import { Select } from "../ui/Select";
import { CATEGORIAS } from "../../utils/constants";
import { formatCategoria } from "../../utils/formatters";

interface ProdutoFormProps {
  initialData?: Produto;
  onSubmit: (data: ProdutoCreate | ProdutoUpdate) => Promise<void>;
  onCancel: () => void;
  isLoading?: boolean;
}

interface FormErrors {
  nome_produto?: string;
  categoria_produto?: string;
}

function SectionTitle({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <p
      className="text-xs font-semibold uppercase tracking-wider mb-4"
      style={{ color: "var(--color-text-secondary)" }}
    >
      {children}
    </p>
  );
}

export function ProdutoForm({
  initialData,
  onSubmit,
  onCancel,
  isLoading = false,
}: Readonly<ProdutoFormProps>) {
  const [form, setForm] = useState({
    nome_produto: initialData?.nome_produto ?? "",
    categoria_produto: initialData?.categoria_produto ?? "",
    peso_produto_gramas: initialData?.peso_produto_gramas?.toString() ?? "",
    comprimento_centimetros: initialData?.comprimento_centimetros?.toString() ?? "",
    altura_centimetros: initialData?.altura_centimetros?.toString() ?? "",
    largura_centimetros: initialData?.largura_centimetros?.toString() ?? "",
  });
  const [errors, setErrors] = useState<FormErrors>({});

  const validate = (): boolean => {
    const newErrors: FormErrors = {};
    if (!form.nome_produto.trim()) newErrors.nome_produto = "Nome é obrigatório";
    if (!form.categoria_produto) newErrors.categoria_produto = "Categoria é obrigatória";
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const parseFloat_ = (v: string) => (v === "" ? null : Number.parseFloat(v));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;
    await onSubmit({
      nome_produto: form.nome_produto.trim(),
      categoria_produto: form.categoria_produto,
      peso_produto_gramas: parseFloat_(form.peso_produto_gramas),
      comprimento_centimetros: parseFloat_(form.comprimento_centimetros),
      altura_centimetros: parseFloat_(form.altura_centimetros),
      largura_centimetros: parseFloat_(form.largura_centimetros),
    });
  };

  const categoriaOptions = CATEGORIAS.map((c) => ({ value: c, label: formatCategoria(c) }));

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Informações Básicas */}
      <div>
        <SectionTitle>Informações Básicas</SectionTitle>
        <div className="space-y-4">
          <Input
            id="nome_produto"
            label="Nome do Produto *"
            value={form.nome_produto}
            onChange={(e) => setForm((f) => ({ ...f, nome_produto: e.target.value }))}
            error={errors.nome_produto}
            placeholder="Ex: Perfume Floral 100ml"
          />
          <Select
            id="categoria_produto"
            label="Categoria *"
            value={form.categoria_produto}
            options={categoriaOptions}
            placeholder="Selecionar categoria..."
            onChange={(e) => setForm((f) => ({ ...f, categoria_produto: e.target.value }))}
          />
          {errors.categoria_produto && (
            <p className="text-xs text-rose-400 -mt-2">{errors.categoria_produto}</p>
          )}
        </div>
      </div>

      {/* Separator */}
      <hr style={{ borderColor: "var(--color-border)" }} />

      {/* Dimensões */}
      <div>
        <SectionTitle>Dimensões</SectionTitle>
        <div className="grid grid-cols-2 gap-4">
          <Input
            id="peso"
            label="Peso (g)"
            type="number"
            min="0"
            step="0.1"
            value={form.peso_produto_gramas}
            onChange={(e) => setForm((f) => ({ ...f, peso_produto_gramas: e.target.value }))}
            placeholder="Ex: 850"
          />
          <Input
            id="comprimento"
            label="Comprimento (cm)"
            type="number"
            min="0"
            step="0.1"
            value={form.comprimento_centimetros}
            onChange={(e) => setForm((f) => ({ ...f, comprimento_centimetros: e.target.value }))}
            placeholder="Ex: 44"
          />
          <Input
            id="altura"
            label="Altura (cm)"
            type="number"
            min="0"
            step="0.1"
            value={form.altura_centimetros}
            onChange={(e) => setForm((f) => ({ ...f, altura_centimetros: e.target.value }))}
            placeholder="Ex: 4"
          />
          <Input
            id="largura"
            label="Largura (cm)"
            type="number"
            min="0"
            step="0.1"
            value={form.largura_centimetros}
            onChange={(e) => setForm((f) => ({ ...f, largura_centimetros: e.target.value }))}
            placeholder="Ex: 13"
          />
        </div>
      </div>

      {/* Separator + actions */}
      <hr style={{ borderColor: "var(--color-border)" }} />
      <div className="flex justify-end gap-3">
        <Button type="button" variant="secondary" onClick={onCancel}>
          Cancelar
        </Button>
        <Button type="submit" isLoading={isLoading}>
          {initialData ? "Salvar alterações" : "Criar produto"}
        </Button>
      </div>
    </form>
  );
}
