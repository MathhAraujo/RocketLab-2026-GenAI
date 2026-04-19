type ErrorMessageProps = {
  mensagem: string;
  variant?: 'error' | 'warning';
};

const STYLES = {
  error: 'bg-red-50 text-red-700 dark:bg-red-900/20 dark:text-red-400',
  warning: 'bg-yellow-50 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-300',
} as const;

export function ErrorMessage({ mensagem, variant = 'error' }: ErrorMessageProps): JSX.Element {
  return (
    <p role="alert" className={`rounded-lg p-3 text-sm ${STYLES[variant]}`}>
      {mensagem}
    </p>
  );
}
