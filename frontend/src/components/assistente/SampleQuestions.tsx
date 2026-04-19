import type { JSX } from 'react';

const SAMPLE_QUESTIONS: readonly string[] = [
  'Top 10 produtos mais vendidos',
  'Qual a distribuição de pedidos por status?',
  'Quais categorias de produto têm maior receita total?',
  'Qual a média de avaliação dos pedidos por categoria?',
  'Quantos pedidos foram feitos por estado?',
  'Quais são os 5 vendedores com maior volume de vendas?',
  'Qual o percentual de pedidos entregues no prazo?',
  'Quais produtos têm avaliação média abaixo de 3?',
  'Qual a receita total por mês?',
  'Qual a receita média por pedido agrupada por estado?',
] as const;

type SampleQuestionsProps = {
  onPick: (pergunta: string) => void;
  isAdmin: boolean;
};

export default function SampleQuestions({ onPick, isAdmin }: SampleQuestionsProps): JSX.Element {
  return (
    <ul className="flex flex-wrap gap-2" aria-label="Perguntas sugeridas">
      {SAMPLE_QUESTIONS.map((q) => (
        <li key={q}>
          <button
            type="button"
            aria-disabled={!isAdmin}
            disabled={!isAdmin}
            onClick={() => onPick(q)}
            className={[
              'rounded-full border px-3 py-1 text-xs transition-colors',
              'focus:outline-none focus:ring-2 focus:ring-indigo-400 focus:ring-offset-1',
              isAdmin
                ? 'border-indigo-300 text-indigo-700 hover:bg-indigo-50 dark:border-indigo-600 dark:text-indigo-300 dark:hover:bg-indigo-900/30'
                : 'cursor-not-allowed border-gray-200 text-gray-400 dark:border-gray-700 dark:text-gray-600',
            ].join(' ')}
            title={isAdmin ? q : 'Funcionalidade restrita a administradores'}
          >
            {q}
          </button>
        </li>
      ))}
    </ul>
  );
}
