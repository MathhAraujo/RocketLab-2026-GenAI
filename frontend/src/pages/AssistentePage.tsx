import { useState } from 'react';
import { perguntarAoAssistente } from '../api/assistenteApi';
import { ErrorMessage } from '../components/assistente/ErrorMessage';
import { PromptInput } from '../components/assistente/PromptInput';
import { ResultRenderer } from '../components/assistente/ResultRenderer';
import { SQLViewer } from '../components/assistente/SQLViewer';
import { useAuth } from '../hooks/useAuth';
import type { RespostaAssistente } from '../types/assistente';

export function AssistentePage(): JSX.Element {
  const { user } = useAuth();
  const isAdmin = user?.is_admin ?? false;

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
      setResposta(resultado);
    } catch {
      setErroApi('Não foi possível conectar ao servidor. Tente novamente.');
    } finally {
      setCarregando(false);
    }
  };

  return (
    <div className="flex h-full gap-4">
      {/* Sidebar — HistorySidebar (TASK-27) */}
      <aside className="hidden w-56 shrink-0 flex-col gap-2 lg:flex">
        <p className="text-xs font-semibold uppercase tracking-wide text-gray-400 dark:text-gray-500">
          Histórico
        </p>
        <div className="flex-1 rounded-lg border border-gray-200 p-3 dark:border-gray-700" />
      </aside>

      {/* Main area */}
      <main className="flex min-w-0 flex-1 flex-col gap-4">
        {/* Anonymous toggle — AnonymizeToggle (TASK-28) */}
        {isAdmin && (
          <div className="flex items-center gap-2 text-sm">
            <label
              htmlFor="anonimizar"
              className="cursor-pointer select-none text-gray-600 dark:text-gray-300"
            >
              🔒 Modo anônimo
            </label>
            <input
              id="anonimizar"
              type="checkbox"
              checked={anonimizar}
              onChange={(e) => setAnonimizar(e.target.checked)}
              className="h-4 w-4 cursor-pointer rounded accent-indigo-500 focus:ring-2 focus:ring-indigo-400"
            />
          </div>
        )}

        <PromptInput
          value={pergunta}
          onChange={setPergunta}
          onSubmit={() => void handleSubmit()}
          isAdmin={isAdmin}
          isLoading={carregando}
        />

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
            <ResultRenderer visualizacoes={resposta.visualizacoes} />
          </section>
        )}
      </main>
    </div>
  );
}
