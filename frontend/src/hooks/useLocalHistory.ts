import { useCallback, useEffect, useState } from 'react';

const STORAGE_KEY = 'assistente:historico';
const MAX_HISTORICO = 10;

type EntradaHistorico = {
  pergunta: string;
  timestamp: number;
};

type UseLocalHistoryResult = {
  historico: EntradaHistorico[];
  adicionar: (pergunta: string) => void;
  limpar: () => void;
};

export function useLocalHistory(): UseLocalHistoryResult {
  const [historico, setHistorico] = useState<EntradaHistorico[]>(() => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      return raw ? (JSON.parse(raw) as EntradaHistorico[]) : [];
    } catch {
      return [];
    }
  });

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(historico));
  }, [historico]);

  const adicionar = useCallback((pergunta: string) => {
    setHistorico((prev) => {
      const sem_duplicata = prev.filter((e) => e.pergunta !== pergunta);
      const atualizado = [{ pergunta, timestamp: Date.now() }, ...sem_duplicata];
      return atualizado.slice(0, MAX_HISTORICO);
    });
  }, []);

  const limpar = useCallback(() => {
    localStorage.removeItem(STORAGE_KEY);
    setHistorico([]);
  }, []);

  return { historico, adicionar, limpar };
}
