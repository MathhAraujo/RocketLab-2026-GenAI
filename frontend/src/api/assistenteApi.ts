import type { PerguntaRequest, RespostaAssistente } from '../types/assistente';
import api from './client';

type SaudeResponse = {
  status: string;
  gemini_configurado: boolean;
  banco_acessivel: boolean;
};

export async function perguntarAoAssistente(req: PerguntaRequest): Promise<RespostaAssistente> {
  const response = await api.post<RespostaAssistente>('/assistente/perguntar', req);
  return response.data;
}

export async function verificarSaude(): Promise<SaudeResponse> {
  const response = await api.get<SaudeResponse>('/assistente/saude');
  return response.data;
}
