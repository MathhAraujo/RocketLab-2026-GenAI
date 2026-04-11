import type { Produto, ProdutoCreate, ProdutoDetalhes, ProdutoUpdate } from '../types'

const BASE_URL = '/api'

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json', ...init?.headers },
    ...init,
  })
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error((error as { detail?: string }).detail ?? 'Erro na requisição')
  }
  if (res.status === 204) return undefined as T
  return res.json() as Promise<T>
}

export const produtosApi = {
  listar: (busca?: string): Promise<Produto[]> => {
    const params = busca ? `?busca=${encodeURIComponent(busca)}` : ''
    return request<Produto[]>(`/produtos${params}`)
  },

  obter: (id: string): Promise<ProdutoDetalhes> =>
    request<ProdutoDetalhes>(`/produtos/${id}`),

  criar: (data: ProdutoCreate): Promise<Produto> =>
    request<Produto>('/produtos', { method: 'POST', body: JSON.stringify(data) }),

  atualizar: (id: string, data: ProdutoUpdate): Promise<Produto> =>
    request<Produto>(`/produtos/${id}`, { method: 'PUT', body: JSON.stringify(data) }),

  deletar: (id: string): Promise<void> =>
    request<void>(`/produtos/${id}`, { method: 'DELETE' }),
}
