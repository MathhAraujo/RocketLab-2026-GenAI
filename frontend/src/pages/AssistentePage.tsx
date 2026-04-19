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
  const [sidebarAberta, setSidebarAberta] = useState(false);

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

  const handlePickQuestion = (q: string) => {
    setPergunta(q);
    setSidebarAberta(false);
  };

  return (
    <div className="relative flex h-full min-w-0 gap-4">
      {/* Mobile overlay backdrop */}
      {sidebarAberta && (
        <div
          className="fixed inset-0 z-20 bg-black/40 md:hidden"
          aria-hidden="true"
          onClick={() => setSidebarAberta(false)}
        />
      )}

      {/* Sidebar — fixed overlay on mobile, static column on md+ */}
      <aside
        className={[
          'fixed inset-y-0 left-0 z-30 w-64 bg-white p-3 shadow-lg transition-transform dark:bg-gray-900',
          'md:static md:z-auto md:w-56 md:translate-x-0 md:bg-transparent md:p-0 md:shadow-none',
          sidebarAberta ? 'translate-x-0' : '-translate-x-full',
        ].join(' ')}
      >
        <div className="h-full rounded-lg border border-gray-200 p-3 dark:border-gray-700">
          <HistorySidebar
            historico={historico}
            onPick={handlePickQuestion}
            onLimpar={limpar}
            onClose={() => setSidebarAberta(false)}
          />
        </div>
      </aside>

      {/* Main area */}
      <main className="flex min-w-0 flex-1 flex-col gap-4">
        {/* Mobile header row: hamburger + toggle */}
        <div className="flex items-center gap-2 md:hidden">
          <button
            type="button"
            aria-label="Abrir histórico"
            onClick={() => setSidebarAberta(true)}
            className="rounded-lg border border-gray-300 p-2 text-gray-600 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-400 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-800"
          >
            ☰
          </button>
          {isAdmin && <AnonymizeToggle checked={anonimizar} onChange={setAnonimizar} />}
        </div>

        {/* Desktop-only toggle (md and above) */}
        {isAdmin && (
          <div className="hidden md:block">
            <AnonymizeToggle checked={anonimizar} onChange={setAnonimizar} />
          </div>
        )}

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
