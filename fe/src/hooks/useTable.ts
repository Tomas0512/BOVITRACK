import { useMemo, useState } from "react";

interface UseTableOptions<T> {
  initialKey?: string | null;
  getValue: (item: T, key: string) => string | number;
}

/**
 * Reutilizable para paginar y ordenar una lista de clientes en el frontend.
 * Aplica paginación (página de `perPage`) y orden por columna sobre un array.
 */
export function useTable<T>(items: T[], { initialKey = null, getValue }: UseTableOptions<T>) {
  const [page, setPage] = useState(1);
  const perPage = 8;
  const [sortKey, setSortKey] = useState<string | null>(initialKey);
  const [sortDir, setSortDir] = useState<"asc" | "desc">("asc");

  const sorted = useMemo(() => {
    if (!sortKey) return items;
    const copy = [...items];
    copy.sort((a, b) => {
      const av = getValue(a, sortKey);
      const bv = getValue(b, sortKey);
      if (av < bv) return sortDir === "asc" ? -1 : 1;
      if (av > bv) return sortDir === "asc" ? 1 : -1;
      return 0;
    });
    return copy;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [items, sortKey, sortDir]);

  const total = sorted.length;
  const pageCount = Math.max(1, Math.ceil(total / perPage));
  const safePage = Math.min(page, pageCount);
  const paginated = sorted.slice((safePage - 1) * perPage, safePage * perPage);
  const start = total === 0 ? 0 : (safePage - 1) * perPage + 1;
  const end = Math.min(safePage * perPage, total);

  const handleSort = (key: string) => {
    if (sortKey === key) setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    else {
      setSortKey(key);
      setSortDir("asc");
    }
    setPage(1);
  };

  return { page: safePage, pageCount, start, end, total, paginated, setPage, sortKey, sortDir, handleSort };
}
