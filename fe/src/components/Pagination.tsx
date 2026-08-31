interface Props {
  page: number;
  pageCount: number;
  start: number;
  end: number;
  total: number;
  onChange: (page: number) => void;
}

export default function Pagination({ page, pageCount, start, end, total, onChange }: Props) {
  // Con una sola página no es necesario mostrar el control.
  if (pageCount <= 1) return null;

  return (
    <div className="mt-4 flex flex-wrap items-center justify-between gap-2 text-sm text-text-muted">
      <span>
        Mostrando {start}–{end} de {total}
      </span>
      <div className="flex items-center gap-2">
        <button
          type="button"
          disabled={page <= 1}
          onClick={() => onChange(page - 1)}
          className="rounded-lg border border-border px-3 py-1 text-sm font-medium text-text-secondary transition-colors hover:bg-surface-alt disabled:cursor-not-allowed disabled:opacity-40"
        >
          ← Anterior
        </button>
        <span className="min-w-14 text-center">
          {page} / {pageCount}
        </span>
        <button
          type="button"
          disabled={page >= pageCount}
          onClick={() => onChange(page + 1)}
          className="rounded-lg border border-border px-3 py-1 text-sm font-medium text-text-secondary transition-colors hover:bg-surface-alt disabled:cursor-not-allowed disabled:opacity-40"
        >
          Siguiente →
        </button>
      </div>
    </div>
  );
}
