import axios from 'axios';
import { useState } from 'react';
import { perguntarAoAssistente } from '../api/assistenteApi';
import { AnonimizacaoLegenda } from '../components/assistente/AnonimizacaoLegenda';
import AnonymizeToggle from '../components/assistente/AnonymizeToggle';
import { ErrorMessage } from '../components/assistente/ErrorMessage';
import HistoryDropdown from '../components/assistente/HistoryDropdown';
import { PromptInput } from '../components/assistente/PromptInput';
import { ResultRenderer } from '../components/assistente/ResultRenderer';
import SampleQuestions from '../components/assistente/SampleQuestions';
import { SQLViewer } from '../components/assistente/SQLViewer';
import { useAuth } from '../hooks/useAuth';
import { useLocalHistory } from '../hooks/useLocalHistory';
import type { EntradaHistorico } from '../hooks/useLocalHistory';
import type { RespostaAssistente } from '../types/assistente';

type ApiError = { mensagem: string; variant: 'error' | 'warning' };

export function AssistentePage(): JSX.Element {
  const { user } = useAuth();
  const isAdmin = user?.is_admin ?? false;
  const { historico, adicionar, limpar } = useLocalHistory();

  const [pergunta, setPergunta] = useState('');
  const [anonimizar, setAnonimizar] = useState(true);
  const [resposta, setResposta] = useState<RespostaAssistente | null>(null);
  const [erroApi, setErroApi] = useState<ApiError | null>(null);
  const [carregando, setCarregando] = useState(false);

  const handleSubmit = async () => {
    if (!pergunta.trim() || carregando) return;
    setCarregando(true);
    setErroApi(null);
    setResposta(null);
    try {
      const resultado = await perguntarAoAssistente({ pergunta, anonimizar });
      if (!resultado.erro_amigavel) adicionar(pergunta, anonimizar, resultado);
      setResposta(resultado);
    } catch (err) {
      if (axios.isAxiosError<{ detail?: string }>(err) && err.response) {
        setErroApi({
          mensagem:
            err.response.data?.detail ?? 'Não foi possível conectar ao servidor. Tente novamente.',
          variant: err.response.status === 429 ? 'warning' : 'error',
        });
      } else {
        setErroApi({
          mensagem: 'Não foi possível conectar ao servidor. Tente novamente.',
          variant: 'error',
        });
      }
    } finally {
      setCarregando(false);
    }
  };

  const handlePickHistorico = (entrada: EntradaHistorico) => {
    setPergunta(entrada.pergunta);
    setAnonimizar(entrada.anonimizar);
    setResposta(entrada.resposta);
    setErroApi(null);
  };

  return (
    <main className="flex min-w-0 flex-1 flex-col gap-4">
      {isAdmin && <AnonymizeToggle checked={anonimizar} onChange={setAnonimizar} />}

      <HistoryDropdown historico={historico} onPick={handlePickHistorico} onLimpar={limpar} />

      <PromptInput
        value={pergunta}
        onChange={setPergunta}
        onSubmit={() => void handleSubmit()}
        isAdmin={isAdmin}
        isLoading={carregando}
      />

      <SampleQuestions onPick={setPergunta} isAdmin={isAdmin} />

      {erroApi && <ErrorMessage mensagem={erroApi.mensagem} variant={erroApi.variant} />}

      {resposta?.erro_amigavel && (
        <ErrorMessage mensagem={resposta.erro_amigavel} variant="warning" />
      )}

      {resposta && !resposta.erro_amigavel && (
        <section aria-label="Resultado" className="flex flex-col gap-4">
          <SQLViewer sql={resposta.sql_gerado} />
          {resposta.explicacao && (
            <p className="text-sm text-gray-700 dark:text-gray-300">{resposta.explicacao}</p>
          )}
          <ResultRenderer visualizacoes={resposta.visualizacoes} isAdmin={isAdmin} />
          {resposta.traducao_anonimizacao &&
            Object.keys(resposta.traducao_anonimizacao).length > 0 && (
              <AnonimizacaoLegenda traducao={resposta.traducao_anonimizacao} />
            )}
        </section>
      )}
    </main>
  );
}
