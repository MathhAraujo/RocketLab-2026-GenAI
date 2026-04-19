import { useState } from 'react';
import { perguntarAoAssistente } from '../api/assistenteApi';
import AnonymizeToggle from '../components/assistente/AnonymizeToggle';
import { ErrorMessage } from '../components/assistente/ErrorMessage';
import HistorySidebar from '../components/assistente/HistorySidebar';
import { PromptInput } from '../components/assistente/PromptInput';
import { ResultRenderer } from '../components/assistente/ResultRenderer';
import SampleQuestions from '../components/assistente/SampleQuestions';
import { SQLViewer } from '../components/assistente/SQLViewer';
import { useAuth } from '../hooks/useAuth';
import { useLocalHistory } from '../hooks/useLocalHistory';
import type { RespostaAssistente } from '../types/assistente';

export function AssistentePage(): JSX.Element {
  const { user } = useAuth();
  const isAdmin = user?.is_admin ?? false;
  const { historico, adicionar, limpar } = useLocalHistory();

  const [pergunta, setPergunta] = useState('');
  const [anonimizar, setAnonimizar] = useState(false);
  const [resposta, setResposta] = useState<RespostaAssistente | null>(null);
  const [erroApi, setErroApi] = useState<string | null>(null);
  const [carregando, setCarregando] = useState(false);

  const handleSubmit = async () => {
    if (!pergunta.trim() || carregando) return;
    setCarregando(true);
    setErroApi(null);
    setResposta(null);
    try {
      const resultado = await perguntarAoAssistente({ pergunta, anonimizar });
      if (!resultado.erro_amigavel) adicionar(pergunta);
      setResposta(resultado);
    } catch {
      setErroApi('Não foi possível conectar ao servidor. Tente novamente.');
    } finally {
      setCarregando(false);
    }
  };

  return (
    <div className="flex h-full gap-4">
      {/* Sidebar */}
      <aside className="hidden w-56 shrink-0 lg:block">
        <div className="rounded-lg border border-gray-200 p-3 dark:border-gray-700">
          <HistorySidebar historico={historico} onPick={setPergunta} onLimpar={limpar} />
        </div>
      </aside>

      {/* Main area */}
      <main className="flex min-w-0 flex-1 flex-col gap-4">
        {isAdmin && <AnonymizeToggle checked={anonimizar} onChange={setAnonimizar} />}

        <PromptInput
          value={pergunta}
          onChange={setPergunta}
          onSubmit={() => void handleSubmit()}
          isAdmin={isAdmin}
          isLoading={carregando}
        />

        <SampleQuestions onPick={setPergunta} isAdmin={isAdmin} />

        {erroApi && <ErrorMessage mensagem={erroApi} />}

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
          </section>
        )}
      </main>
    </div>
  );
}
