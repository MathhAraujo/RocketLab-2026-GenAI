import { useCallback, useEffect, useState } from 'react';
import type { RespostaAssistente, TabelaVisualizacao, Visualizacao } from '../types/assistente';

const STORAGE_KEY = 'assistente:historico';
const MAX_HISTORICO = 10;
const MAX_STORED_ROWS = 100;

type EntradaHistorico = {
  pergunta: string;
  anonimizar: boolean;
  resposta: RespostaAssistente;
  timestamp: number;
};

type UseLocalHistoryResult = {
  historico: EntradaHistorico[];
  adicionar: (pergunta: string, anonimizar: boolean, resposta: RespostaAssistente) => void;
  limpar: () => void;
};

function capTabela(vis: Visualizacao): Visualizacao {
  if (vis.tipo !== 'tabela') return vis;
  const tabela = vis as TabelaVisualizacao;
  return tabela.linhas.length <= MAX_STORED_ROWS
    ? tabela
    : { ...tabela, linhas: tabela.linhas.slice(0, MAX_STORED_ROWS) };
}

function capRows(resposta: RespostaAssistente): RespostaAssistente {
  return { ...resposta, visualizacoes: resposta.visualizacoes.map(capTabela) };
}

function isEntradaValida(value: unknown): value is EntradaHistorico {
  if (typeof value !== 'object' || value === null) return false;
  const obj = value as Record<string, unknown>;
  return (
    typeof obj['pergunta'] === 'string' &&
    typeof obj['anonimizar'] === 'boolean' &&
    typeof obj['resposta'] === 'object' &&
    obj['resposta'] !== null &&
    typeof obj['timestamp'] === 'number'
  );
}

function loadFromStorage(): EntradaHistorico[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    const parsed: unknown = JSON.parse(raw);
    if (!Array.isArray(parsed)) return [];
    return parsed.filter(isEntradaValida);
  } catch {
    return [];
  }
}

function saveToStorage(entries: EntradaHistorico[]): EntradaHistorico[] {
  let current = entries;
  while (current.length > 0) {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(current));
      return current;
    } catch (err) {
      const isDomException = err instanceof DOMException;
      const isQuota =
        isDomException &&
        (err.name === 'QuotaExceededError' || err.name === 'NS_ERROR_DOM_QUOTA_REACHED');
      if (!isQuota) break;
      current = current.slice(0, -1);
    }
  }
  console.warn('[useLocalHistory] Quota esgotada — histórico limpo.');
  localStorage.removeItem(STORAGE_KEY);
  return [];
}

export function useLocalHistory(): UseLocalHistoryResult {
  const [historico, setHistorico] = useState<EntradaHistorico[]>(loadFromStorage);

  useEffect(() => {
    const saved = saveToStorage(historico);
    if (saved.length !== historico.length) setHistorico(saved);
  }, [historico]);

  const adicionar = useCallback(
    (pergunta: string, anonimizar: boolean, resposta: RespostaAssistente) => {
      setHistorico((prev) => {
        const semDuplicata = prev.filter((e) => e.pergunta !== pergunta);
        const entrada: EntradaHistorico = {
          pergunta,
          anonimizar,
          resposta: capRows(resposta),
          timestamp: Date.now(),
        };
        return [entrada, ...semDuplicata].slice(0, MAX_HISTORICO);
      });
    },
    [],
  );

  const limpar = useCallback(() => {
    localStorage.removeItem(STORAGE_KEY);
    setHistorico([]);
  }, []);

  return { historico, adicionar, limpar };
}

export type { EntradaHistorico };
