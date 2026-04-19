import { Link } from 'react-router-dom';
import { Button } from '../components/ui/Button';

export function NotFoundPage(): JSX.Element {
  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center gap-4 text-center">
      <p className="text-7xl font-black text-violet-600 opacity-60">404</p>
      <h1 className="text-2xl font-bold text-slate-100">Página não encontrada</h1>
      <p className="text-slate-400">A página que você tentou acessar não existe.</p>
      <Link to="/catalogo">
        <Button>Voltar ao catálogo</Button>
      </Link>
    </div>
  );
}
