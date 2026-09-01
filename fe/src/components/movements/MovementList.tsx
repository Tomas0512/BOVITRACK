import { useEffect, useMemo, useState } from "react";
import { Plus, AlertTriangle, ArrowUpDown } from "lucide-react";
import { listMovements, type MovementResponse } from "../../api/movements";
import { listBovines, type BovineResponse } from "../../api/bovines";
import { getApiErrorMessage } from "../../api/errors";
import Pagination from "../Pagination";
import MovementFormModal from "./MovementFormModal";

const TYPE_BADGE: Record<string, string> = {
  compra: "bg-green-100 text-green-800",
  venta: "bg-red-100 text-red-800",
  traslado: "bg-blue-100 text-blue-800",
  nacimiento: "bg-purple-100 text-purple-800",
  muerte: "bg-surface-alt text-text-secondary",
};

const TYPE_LABEL: Record<string, string> = {
  compra: "Compra",
  venta: "Venta",
  traslado: "Traslado",
  nacimiento: "Nacimiento",
  muerte: "Muerte",
};

interface Props {
  farmId: string;
}

export default function MovementList({ farmId }: Props) {
  const [movements, setMovements] = useState<MovementResponse[]>([]);
  const [bovines, setBovines] = useState<BovineResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showModal, setShowModal] = useState(false);
  const [filterType, setFilterType] = useState("");
  const [sortKey, setSortKey] = useState<string>("movement_date");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("desc");
  const [page, setPage] = useState(1);
  const perPage = 8;

  const handleSort = (key: string) => {
    if (sortKey === key) {
      setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    } else {
      setSortKey(key);
      setSortDir("asc");
    }
    setPage(1);
  };

  const getValue = (m: MovementResponse, key: string): string | number => {
    const v = (m as unknown as Record<string, unknown>)[key];
    return typeof v === "number" ? v : String(v ?? "");
  };

  const { total, pageCount, safePage, paginated, start, end } = useMemo(() => {
    const arr = [...movements];
    arr.sort((a, b) => {
      const av = getValue(a, sortKey);
      const bv = getValue(b, sortKey);
      if (av < bv) return sortDir === "asc" ? -1 : 1;
      if (av > bv) return sortDir === "asc" ? 1 : -1;
      return 0;
    });
    const count = arr.length;
    const pages = Math.max(1, Math.ceil(count / perPage));
    const p = Math.min(page, pages);
    return {
      total: count,
      pageCount: pages,
      safePage: p,
      paginated: arr.slice((p - 1) * perPage, p * perPage),
      start: count === 0 ? 0 : (p - 1) * perPage + 1,
      end: Math.min(p * perPage, count),
    };
  }, [movements, sortKey, sortDir, page]);

  const fetchData = async () => {
    try {
      const [data, bov] = await Promise.all([
        listMovements(farmId, filterType ? { movement_type: filterType } : undefined),
        listBovines(farmId),
      ]);
      setMovements(data);
      setBovines(bov);
    } catch (err: unknown) {
      setError(getApiErrorMessage(err, "Error al cargar movimientos"));
    } finally {
      setLoading(false);
    }
  };

  const bovineLabel = useMemo(() => {
    const map = new Map<string, string>();
    for (const b of bovines) map.set(b.id, b.identification_number + (b.name ? ` · ${b.name}` : ""));
    return (id: string | null) => (id ? map.get(id) ?? "—" : "—");
  }, [bovines]);

  useEffect(() => { setPage(1); }, [farmId, filterType]);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => { fetchData(); }, [farmId, filterType]);

  return (
    <div className="mt-6 rounded-2xl bg-surface p-6 shadow-sm">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-2">
        <h2 className="text-lg font-bold text-text-primary">Movimientos del hato</h2>
        <div className="flex items-center gap-2">
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="rounded-lg border border-border px-3 py-1.5 text-sm focus:border-primary focus:outline-none"
          >
            <option value="">Todos los tipos</option>
            {Object.entries(TYPE_LABEL).map(([k, v]) => (
              <option key={k} value={k}>{v}</option>
            ))}
          </select>
          <button onClick={() => setShowModal(true)}
            className="inline-flex items-center gap-1.5 rounded-lg bg-primary px-4 py-1.5 text-sm font-bold text-white hover:bg-primary-light">
            <Plus size={16} />
            Registrar
          </button>
        </div>
      </div>

      {error && (
        <div className="mb-4 flex items-center gap-2 rounded-lg bg-red-50 p-3 text-sm text-red-700">
          <AlertTriangle size={16} /> {error}
          <button onClick={() => setError("")} className="ml-auto font-bold">X</button>
        </div>
      )}

      {loading ? (
        <div className="flex justify-center py-8">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
        </div>
      ) : movements.length === 0 ? (
        <div className="rounded-xl border border-dashed border-border py-8 text-center text-sm text-text-muted">
          <ArrowUpDown size={32} className="mx-auto mb-2 text-text-muted" />
          No hay movimientos registrados aún
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border text-left text-xs font-semibold uppercase tracking-wide text-text-muted">
                <th className="pb-2 pr-4">
                  <button onClick={() => handleSort("movement_type")} className="flex items-center gap-1 uppercase">
                    Tipo {sortKey === "movement_type" && (sortDir === "asc" ? "▲" : "▼")}
                  </button>
                </th>
                <th className="pb-2 pr-4">
                  <button onClick={() => handleSort("movement_date")} className="flex items-center gap-1 uppercase">
                    Fecha {sortKey === "movement_date" && (sortDir === "asc" ? "▲" : "▼")}
                  </button>
                </th>
                <th className="pb-2 pr-4">Bovino</th>
                <th className="pb-2 pr-4">
                  <button onClick={() => handleSort("price")} className="flex items-center gap-1 uppercase">
                    Valor {sortKey === "price" && (sortDir === "asc" ? "▲" : "▼")}
                  </button>
                </th>
                <th className="pb-2 pr-4">Contraparte</th>
                <th className="pb-2 pr-4">Motivo</th>
                <th className="pb-2 pr-4 text-right">Registro</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {paginated.map((m) => (
                <tr key={m.id} className="hover:bg-surface-alt">
                  <td className="py-3 pr-4">
                    <span className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-semibold ${TYPE_BADGE[m.movement_type] || "bg-surface-alt text-text-secondary"}`}>
                      {TYPE_LABEL[m.movement_type] || m.movement_type}
                    </span>
                  </td>
                  <td className="py-3 pr-4 text-text-secondary">{new Date(m.movement_date).toLocaleDateString("es-CO")}</td>
                  <td className="py-3 pr-4 text-text-secondary">{bovineLabel(m.bovine_id)}</td>
                  <td className="py-3 pr-4 text-text-secondary">{m.price != null ? `$${Number(m.price).toLocaleString("es-CO")}` : "—"}</td>
                  <td className="py-3 pr-4 text-text-secondary">{m.counterparty_name || "—"}</td>
                  <td className="max-w-[200px] truncate py-3 pr-4 text-text-muted">{m.reason || "—"}</td>
                  <td className="py-3 pr-4 text-right text-xs text-text-muted">Inmutable</td>
                </tr>
              ))}
            </tbody>
          </table>
          <Pagination
            page={safePage}
            pageCount={pageCount}
            start={start}
            end={end}
            total={total}
            onChange={(p) => setPage(p)}
          />
        </div>
      )}

      {showModal && (
        <MovementFormModal
          farmId={farmId}
          onSuccess={() => { setShowModal(false); fetchData(); }}
          onClose={() => setShowModal(false)}
        />
      )}
    </div>
  );
}
