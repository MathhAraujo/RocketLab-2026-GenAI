import { type ReactNode, useEffect } from 'react';
import { X } from 'lucide-react';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: ReactNode;
  footer?: ReactNode;
}

export function Modal({
  isOpen,
  onClose,
  title,
  children,
  footer,
}: Readonly<ModalProps>): JSX.Element | null {
  useEffect(() => {
    if (!isOpen) return;
    const onKey = (e: KeyboardEvent) => e.key === 'Escape' && onClose();
    document.addEventListener('keydown', onKey);
    return () => document.removeEventListener('keydown', onKey);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div
      role="presentation"
      className="fixed inset-0 z-50 flex items-center justify-center p-4 backdrop-blur-sm"
      style={{ background: 'rgba(0,0,0,0.65)' }}
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
      onKeyDown={(e) => e.key === 'Escape' && onClose()}
    >
      <div
        role="dialog"
        aria-modal
        aria-label={title}
        className="w-full max-w-md rounded-2xl shadow-2xl"
        style={{
          background: 'var(--color-bg-surface)',
          border: '1px solid var(--color-border)',
        }}
      >
        <div
          className="flex items-center justify-between px-6 py-4"
          style={{ borderBottom: '1px solid var(--color-border)' }}
        >
          <h2 className="text-base font-semibold" style={{ color: 'var(--color-text-primary)' }}>
            {title}
          </h2>
          <button
            onClick={onClose}
            className="rounded-md p-1 transition-colors hover:bg-zinc-700/50"
            style={{ color: 'var(--color-text-secondary)' }}
          >
            <X size={18} />
          </button>
        </div>
        <div className="px-6 py-4 text-sm" style={{ color: 'var(--color-text-secondary)' }}>
          {children}
        </div>
        {footer && (
          <div
            className="flex justify-end gap-3 px-6 py-4"
            style={{ borderTop: '1px solid var(--color-border)' }}
          >
            {footer}
          </div>
        )}
      </div>
    </div>
  );
}
