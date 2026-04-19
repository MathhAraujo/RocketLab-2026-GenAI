import { Plus } from 'lucide-react';
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { createProduto, getCategorias } from '../api/produtos';
import { ProdutoCard } from '../components/produtos/ProdutoCard';
import { ProdutoFilters } from '../components/produtos/ProdutoFilters';
import { ProdutoForm } from '../components/produtos/ProdutoForm';
import { EmptyState } from '../components/ui/EmptyState';
import { SkeletonCard } from '../components/ui/Loading';
import { Modal } from '../components/ui/Modal';
import { Pagination } from '../components/ui/Pagination';
import { Button } from '../components/ui/Button';
import { useAuth } from '../hooks/useAuth';
import { usePagination } from '../hooks/usePagination';
import { useProdutos } from '../hooks/useProdutos';
import type { ProdutoCreate, ProdutoUpdate } from '../types/produto';

interface NovoProdutoModalProps {
  isOpen: boolean;
  onClose: () => void;
}

function NovoProdutoModal({ isOpen, onClose }: NovoProdutoModalProps): JSX.Element {
  const navigate = useNavigate();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formError, setFormError] = useState('');

  useEffect(() => {
    if (isOpen) setFormError('');
  }, [isOpen]);

  const handleSubmit = async (data: ProdutoCreate | ProdutoUpdate) => {
    setIsSubmitting(true);
    setFormError('');
    try {
      const created = await createProduto(data as ProdutoCreate);
      navigate(`/produtos/${created.id_produto}`);
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
        'Erro ao criar produto';
      setFormError(msg);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Novo Produto">
      {formError && (
        <p
          className="mb-4 rounded-lg px-4 py-2 text-sm"
          style={{
            background: 'rgba(244,63,94,0.1)',
            border: '1px solid rgba(244,63,94,0.3)',
            color: '#f43f5e',
          }}
        >
          {formError}
        </p>
      )}
      <ProdutoForm onSubmit={handleSubmit} onCancel={onClose} isLoading={isSubmitting} />
    </Modal>
  );
}

export function CatalogoPage(): JSX.Element {
  const { user } = useAuth();
  const { page, perPage, goToPage, reset } = usePagination();

  const [search, setSearch] = useState('');
  const [categoria, setCategoria] = useState('');
  const [sortBy, setSortBy] = useState('vendas');
  const [order, setOrder] = useState<'asc' | 'desc'>('desc');
  const [categorias, setCategorias] = useState<string[]>([]);
  const [showForm, setShowForm] = useState(false);

  const { data, isLoading, error } = useProdutos({
    page,
    per_page: perPage,
    search: search || undefined,
    categoria: categoria || undefined,
    sort_by: sortBy,
    order,
  });

  useEffect(() => {
    getCategorias()
      .then(setCategorias)
      .catch(() => {});
  }, []);

  const handleSearchChange = (v: string) => {
    setSearch(v);
    reset();
  };
  const handleCategoriaChange = (v: string) => {
    setCategoria(v);
    reset();
  };

  const renderContent = () => {
    if (isLoading) {
      return (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
          {Array.from({ length: 8 }, (_, i) => (
            <SkeletonCard key={`skeleton-${i}`} />
          ))}
        </div>
      );
    }
    if (data?.items.length === 0) {
      return <EmptyState />;
    }
    return (
      <>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
          {data?.items.map((produto) => (
            <ProdutoCard key={produto.id_produto} produto={produto} />
          ))}
        </div>
        {data && (
          <Pagination
            page={data.page}
            pages={data.pages}
            total={data.total}
            perPage={data.per_page}
            onPageChange={goToPage}
          />
        )}
      </>
    );
  };

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between gap-4">
        <div>
          <h1
            className="text-2xl font-bold"
            style={{ fontFamily: "'Outfit', sans-serif", color: 'var(--color-text-primary)' }}
          >
            Catálogo
          </h1>
          {data && (
            <p className="text-sm mt-0.5" style={{ color: 'var(--color-text-secondary)' }}>
              {data.total.toLocaleString('pt-BR')} produto
              {data.total === 1 ? '' : 's'}
            </p>
          )}
        </div>
        {user?.is_admin && (
          <Button onClick={() => setShowForm(true)}>
            <Plus size={16} />
            Novo Produto
          </Button>
        )}
      </div>

      <ProdutoFilters
        search={search}
        categoria={categoria}
        sortBy={sortBy}
        order={order}
        categorias={categorias}
        onSearchChange={handleSearchChange}
        onCategoriaChange={handleCategoriaChange}
        onSortByChange={(v) => {
          setSortBy(v);
          reset();
        }}
        onOrderChange={(v) => {
          setOrder(v);
          reset();
        }}
      />

      {error && <p className="text-center text-sm text-red-400">{error}</p>}

      {renderContent()}

      {user?.is_admin && <NovoProdutoModal isOpen={showForm} onClose={() => setShowForm(false)} />}
    </div>
  );
}
