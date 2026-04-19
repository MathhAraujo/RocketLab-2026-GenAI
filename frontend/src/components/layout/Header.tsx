import { ShoppingBag, Menu, Sun, Moon } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useTheme } from '../../contexts/ThemeContext';

interface HeaderProps {
  onToggleSidebar?: () => void;
}

export function Header({ onToggleSidebar }: Readonly<HeaderProps>): JSX.Element {
  const { theme, toggleTheme } = useTheme();

  return (
    <header
      className="lg:hidden fixed top-0 left-0 right-0 z-30 flex h-14 items-center justify-between px-4"
      style={{
        background: 'var(--color-bg-surface)',
        borderBottom: '1px solid var(--color-border)',
      }}
    >
      <div className="flex items-center gap-3">
        <button
          onClick={onToggleSidebar}
          className="rounded-lg p-1.5 transition-colors hover:bg-zinc-800/60"
          style={{ color: 'var(--color-text-secondary)' }}
        >
          <Menu size={20} />
        </button>
        <Link to="/catalogo" className="flex items-center gap-2">
          <ShoppingBag size={20} className="text-indigo-500" />
          <span
            className="text-base font-bold"
            style={{ fontFamily: "'Outfit', sans-serif", color: 'var(--color-text-primary)' }}
          >
            Mercadão
          </span>
        </Link>
      </div>
      <button
        onClick={toggleTheme}
        className="rounded-lg p-1.5 transition-colors hover:bg-zinc-800/60"
        style={{ color: 'var(--color-text-secondary)' }}
      >
        {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
      </button>
    </header>
  );
}
