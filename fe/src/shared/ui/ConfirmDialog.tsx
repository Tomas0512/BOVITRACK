import type { ReactNode } from "react";

interface Props {
  open: boolean;
  title: string;
  message?: string;
  confirmLabel?: string;
  cancelLabel?: string;
  danger?: boolean;
  loading?: boolean;
  children?: ReactNode;
  onConfirm: () => void;
  onCancel: () => void;
}

export default function ConfirmDialog({
  open,
  title,
  message,
  confirmLabel = "Confirmar",
  cancelLabel = "Cancelar",
  danger = true,
  loading = false,
  children,
  onConfirm,
  onCancel,
}: Props) {
  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4"
      onClick={onCancel}
    >
      <div
        className="w-full max-w-md rounded-2xl bg-surface p-6 shadow-xl"
        onClick={(e) => e.stopPropagation()}
      >
        <h2 className="mb-2 text-lg font-bold text-primary">{title}</h2>
        {message && <p className="mb-4 text-sm text-text-secondary">{message}</p>}
        {children}
        <div className="flex gap-2 pt-2">
          <button
            type="button"
            onClick={onCancel}
            className="flex-1 rounded-lg border border-border px-4 py-2 text-sm font-medium text-text-secondary hover:bg-surface-alt"
          >
            {cancelLabel}
          </button>
          <button
            type="button"
            onClick={onConfirm}
            disabled={loading}
            className={`flex-1 rounded-lg px-4 py-2 text-sm font-bold text-white disabled:opacity-60 ${
              danger ? "bg-red-600 hover:bg-red-700" : "bg-primary hover:bg-primary-light"
            }`}
          >
            {loading ? "Procesando…" : confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}
