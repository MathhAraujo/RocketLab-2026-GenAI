import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { produtosApi } from '../services/api'
import type { ProdutoDetalhes } from '../types'

export default function ProductDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [produto, setProduto] = useState<ProdutoDetalhes | null>(null)
  const [loading, setLoading] = useState(true)
  const [erro, setErro] = useState<string | null>(null)

  useEffect(() => {
    if (!id) return
    produtosApi
      .obter(id)
      .then(setProduto)
      .catch((e: unknown) => {
        setErro(e instanceof Error ? e.message : 'Erro ao carregar produto')
      })
      .finally(() => setLoading(false))
  }, [id])

  const handleDeletar = async () => {
    if (!id || !confirm('Deseja realmente remover este produto?')) return
    await produtosApi.deletar(id)
    navigate('/')
  }

  if (loading) return <p>Carregando…</p>
  if (erro) return <p style={{ color: 'red' }}>{erro}</p>
  if (!produto) return null

  return (
    <main>
      <Link to="/">← Voltar ao catálogo</Link>

      <h1>{produto.nome_produto}</h1>
      <p>Categoria: {produto.categoria_produto}</p>

      <h2>Medidas</h2>
      <ul>
        <li>Peso: {produto.peso_produto_gramas ?? '—'} g</li>
        <li>Comprimento: {produto.comprimento_centimetros ?? '—'} cm</li>
        <li>Altura: {produto.altura_centimetros ?? '—'} cm</li>
        <li>Largura: {produto.largura_centimetros ?? '—'} cm</li>
      </ul>

      <h2>Vendas</h2>
      <p>
        Total de vendas: {produto.vendas.total_vendas} | Receita: R${' '}
        {produto.vendas.receita_total.toFixed(2)}
      </p>

      <h2>Avaliações</h2>
      <p>
        {produto.avaliacoes.total_avaliacoes} avaliação(ões) — Média:{' '}
        {produto.avaliacoes.media_avaliacao.toFixed(1)} / 5
      </p>

      <hr />
      <button onClick={handleDeletar} style={{ color: 'red' }}>
        Remover produto
      </button>
    </main>
  )
}
