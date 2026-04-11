import { ArrowLeft } from "lucide-react";
import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { createProduto, getProduto, updateProduto } from "../api/produtos";
import { ProdutoForm } from "../components/produtos/ProdutoForm";
import { Loading } from "../components/ui/Loading";
import type { Produto, ProdutoCreate, ProdutoUpdate } from "../types/produto";

export function ProdutoFormPage() {
  const { id } = useParams<{ id?: string }>();
  const navigate = useNavigate();
  const isEditing = Boolean(id);

  const [produto, setProduto] = useState<Produto | null>(null);
  const [isLoading, setIsLoading] = useState(isEditing);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [successMsg, setSuccessMsg] = useState("");
  const [errorMsg, setErrorMsg] = useState("");

  useEffect(() => {
    if (!id) return;
    getProduto(id)
      .then(setProduto)
      .catch(() => navigate("/catalogo"))
      .finally(() => setIsLoading(false));
  }, [id, navigate]);

  const handleSubmit = async (data: ProdutoCreate | ProdutoUpdate) => {
    setIsSubmitting(true);
    setErrorMsg("");
    setSuccessMsg("");
    try {
      if (isEditing && id) {
        await updateProduto(id, data as ProdutoUpdate);
        setSuccessMsg("Produto atualizado com sucesso!");
        setTimeout(() => navigate(`/produtos/${id}`), 1000);
      } else {
        const created = await createProduto(data as ProdutoCreate);
        setSuccessMsg("Produto criado com sucesso!");
        setTimeout(() => navigate(`/produtos/${created.id_produto}`), 1000);
      }
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { detail?: string } } })?.response?.data
          ?.detail ?? "Erro ao salvar produto";
      setErrorMsg(msg);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoading) return <Loading />;

  return (
    <div className="max-w-xl">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <button
          onClick={() => navigate(id ? `/produtos/${id}` : "/catalogo")}
          className="rounded-lg p-1.5 transition-colors hover:bg-zinc-800/60"
          style={{ color: "var(--color-text-secondary)" }}
        >
          <ArrowLeft size={18} />
        </button>
        <h1
          className="text-2xl font-bold"
          style={{ fontFamily: "'Outfit', sans-serif", color: "var(--color-text-primary)" }}
        >
          {isEditing ? "Editar Produto" : "Novo Produto"}
        </h1>
      </div>

      {successMsg && (
        <p
          className="mb-4 rounded-lg px-4 py-2 text-sm"
          style={{
            background: "rgba(52,211,153,0.1)",
            border: "1px solid rgba(52,211,153,0.3)",
            color: "#34d399",
          }}
        >
          {successMsg}
        </p>
      )}
      {errorMsg && (
        <p
          className="mb-4 rounded-lg px-4 py-2 text-sm"
          style={{
            background: "rgba(244,63,94,0.1)",
            border: "1px solid rgba(244,63,94,0.3)",
            color: "#f43f5e",
          }}
        >
          {errorMsg}
        </p>
      )}

      <div
        className="rounded-2xl border p-6 lg:p-8"
        style={{
          background: "var(--color-bg-surface)",
          borderColor: "var(--color-border)",
        }}
      >
        <ProdutoForm
          initialData={produto ?? undefined}
          onSubmit={handleSubmit}
          onCancel={() => navigate(id ? `/produtos/${id}` : "/catalogo")}
          isLoading={isSubmitting}
        />
      </div>
    </div>
  );
}
