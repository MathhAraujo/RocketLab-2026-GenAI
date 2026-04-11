import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { produtosApi } from '../services/api'
import type { Produto } from '../types'

export default function CatalogPage() {
  const [produtos, setProdutos] = useState<Produto[]>([])
  const [busca, setBusca] = useState('')
  const [loading, setLoading] = useState(false)
  const [erro, setErro] = useState<string | null>(null)

  useEffect(() => {
    setLoading(true)
    setErro(null)
    produtosApi
      .listar(busca || undefined)
      .then(setProdutos)
      .catch((e: unknown) => setErro(e instanceof Error ? e.message : 'Erro desconhecido'))
      .finally(() => setLoading(false))
  }, [busca])

  return (
    <main>
      <h1>Catálogo de Produtos</h1>

      <input
        type="search"
        placeholder="Buscar por nome ou categoria…"
        value={busca}
        onChange={(e) => setBusca(e.target.value)}
      />

      {loading && <p>Carregando…</p>}
      {erro && <p style={{ color: 'red' }}>{erro}</p>}

      <ul>
        {produtos.map((p) => (
          <li key={p.id_produto}>
            <Link to={`/produtos/${p.id_produto}`}>
              <strong>{p.nome_produto}</strong> — {p.categoria_produto}
            </Link>
          </li>
        ))}
      </ul>

      {!loading && produtos.length === 0 && <p>Nenhum produto encontrado.</p>}
    </main>
  )
}
