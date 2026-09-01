import { useEffect, useMemo, useState } from "react";
import { listBovines, deleteBovine, type BovineResponse } from "../../api/bovines";
import { listLandPlots, type LandPlotResponse } from "../../api/land_plots";
import { listPaddocks, type PaddockResponse } from "../../api/paddocks";
import { getApiErrorMessage } from "../../api/errors";
import Pagination from "../Pagination";
import ConfirmDialog from "../ConfirmDialog";
import BovineFormModal from "./BovineFormModal";
import { Link } from "react-router-dom";

interface Props {
  farmId: string;
}

const SEX_BADGE: Record<string, string> = {
  macho: "bg-blue-50 text-blue-700",
  hembra: "bg-pink-50 text-pink-700",
};

const STATUS_BADGE: Record<string, string> = {
  activo: "bg-green-50 text-green-700",
  vendido: "bg-surface-alt text-text-secondary",
  muerto: "bg-red-50 text-red-700",
  retirado: "bg-yellow-50 text-yellow-700",
};

export default function BovineList({ farmId }: Props) {
  const [bovines, setBovines] = useState<BovineResponse[]>([]);
  const [landPlots, setLandPlots] = useState<LandPlotResponse[]>([]);
  const [paddocks, setPaddocks] = useState<PaddockResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showModal, setShowModal] = useState(false);
  const [editing, setEditing] = useState<BovineResponse | undefined>();
  const [actionLoading, setActionLoading] = useState<string | null>(null);
  const [filterSex, setFilterSex] = useState("");
  const [sortKey, setSortKey] = useState<string>("identification_number");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("asc");
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

  const getValue = (b: BovineResponse, key: string): string | number => {
    const v = (b as unknown as Record<string, unknown>)[key];
    return typeof v === "number" ? v : String(v ?? "");
  };

  const { total, pageCount, safePage, paginated, start, end } = useMemo(() => {
    const arr = [...bovines];
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
  }, [bovines, sortKey, sortDir, page]);

  const fetchData = async () => {
    setLoading(true);
    setError("");
    try {
      const [b, lp, p] = await Promise.all([
        listBovines(farmId, filterSex ? { sex: filterSex } : {}),
        listLandPlots(farmId, true),
        listPaddocks(farmId),
      ]);
      setBovines(b);
      setLandPlots(lp);
      setPaddocks(p);
    } catch (err: unknown) {
      setError(getApiErrorMessage(err, "No se pudieron cargar los bovinos"));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { setPage(1); }, [farmId, filterSex]);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => { fetchData(); }, [farmId, filterSex]);

  const [toDelete, setToDelete] = useState<BovineResponse | null>(null);

  const handleDelete = async () => {
    if (!toDelete) return;
    setActionLoading(toDelete.id);
    try {
      await deleteBovine(farmId, toDelete.id);
      setToDelete(null);
      await fetchData();
    } catch (err: unknown) {
      setError(getApiErrorMessage(err, "No se pudo eliminar el bovino"));
    } finally {
      setActionLoading(null);
    }
  };

  const handleSuccess = () => {
    setShowModal(false);
    setEditing(undefined);
    fetchData();
  };

  return (
    <div className="mt-6 rounded-2xl bg-surface p-6 shadow-sm">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h2 className="text-lg font-bold text-text-primary">Bovinos</h2>
          <p className="text-xs text-text-muted">{bovines.length} registro{bovines.length !== 1 ? "s" : ""}</p>
        </div>
        <button onClick={() => { setEditing(undefined); setShowModal(true); }}
          className="rounded-lg bg-primary px-4 py-2 text-sm font-bold text-white hover:bg-primary-light">
          + Registrar bovino
        </button>
      </div>

      {/* Filtros */}
      <div className="mb-4 flex gap-2">
        {[{ val: "", label: "Todos" }, { val: "macho", label: "Machos" }, { val: "hembra", label: "Hembras" }].map((f) => (
          <button key={f.val} onClick={() => setFilterSex(f.val)}
            className={`rounded-full px-3 py-1 text-xs font-medium transition-colors ${filterSex === f.val ? "bg-primary text-white" : "bg-surface-alt text-text-secondary hover:bg-border"}`}>
            {f.label}
          </button>
        ))}
      </div>

      {error && <div className="mb-3 rounded-lg bg-red-50 px-4 py-2 text-sm text-red-700">{error}</div>}

      {loading ? (
        <div className="flex justify-center py-8">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
        </div>
      ) : bovines.length === 0 ? (
        <div className="rounded-lg border border-dashed border-border py-10 text-center">
          <p className="text-sm text-text-muted">No hay bovinos registrados</p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border text-left text-xs font-semibold uppercase tracking-wide text-text-muted">
                <th className="pb-2 pr-4">
                  <button onClick={() => handleSort("identification_number")} className="flex items-center gap-1 uppercase">
                    ID {sortKey === "identification_number" && (sortDir === "asc" ? "▲" : "▼")}
                  </button>
                </th>
                <th className="pb-2 pr-4">
                  <button onClick={() => handleSort("name")} className="flex items-center gap-1 uppercase">
                    Nombre {sortKey === "name" && (sortDir === "asc" ? "▲" : "▼")}
                  </button>
                </th>
                <th className="pb-2 pr-4">
                  <button onClick={() => handleSort("sex")} className="flex items-center gap-1 uppercase">
                    Sexo {sortKey === "sex" && (sortDir === "asc" ? "▲" : "▼")}
                  </button>
                </th>
                <th className="pb-2 pr-4">
                  <button onClick={() => handleSort("breed")} className="flex items-center gap-1 uppercase">
                    Raza {sortKey === "breed" && (sortDir === "asc" ? "▲" : "▼")}
                  </button>
                </th>
                <th className="pb-2 pr-4">
                  <button onClick={() => handleSort("status")} className="flex items-center gap-1 uppercase">
                    Estado {sortKey === "status" && (sortDir === "asc" ? "▲" : "▼")}
                  </button>
                </th>
                <th className="pb-2 pr-4">
                  <button onClick={() => handleSort("current_weight")} className="flex items-center gap-1 uppercase">
                    Peso actual {sortKey === "current_weight" && (sortDir === "asc" ? "▲" : "▼")}
                  </button>
                </th>
                <th className="pb-2">Acciones</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {paginated.map((b) => (
                <tr key={b.id} className="hover:bg-surface-alt">
                  <td className="py-3 pr-4 font-mono text-xs text-text-secondary">{b.identification_number}</td>
                  <td className="py-3 pr-4 font-medium text-text-primary">{b.name ?? "—"}</td>
                  <td className="py-3 pr-4">
                    <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${SEX_BADGE[b.sex] ?? "bg-surface-alt text-text-secondary"}`}>
                      {b.sex}
                    </span>
                  </td>
                  <td className="py-3 pr-4 text-text-secondary">{b.breed ?? "—"}</td>
                  <td className="py-3 pr-4">
                    <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${STATUS_BADGE[b.status] ?? "bg-surface-alt text-text-secondary"}`}>
                      {b.status}
                    </span>
                  </td>
                  <td className="py-3 pr-4 text-text-secondary">{b.current_weight ? `${b.current_weight} kg` : "—"}</td>
                  <td className="py-3">
                    <div className="flex gap-2">
                      <Link to={`/farms/${farmId}/bovines/${b.id}`}
                        className="rounded px-2 py-1 text-xs font-medium text-primary hover:bg-primary/10 no-underline">
                        Ver
                      </Link>
                      <button onClick={() => { setEditing(b); setShowModal(true); }}
                        className="rounded px-2 py-1 text-xs font-medium text-text-secondary hover:bg-surface-alt">
                        Editar
                      </button>
                      <button onClick={() => setToDelete(b)} disabled={actionLoading === b.id}
                        className="rounded px-2 py-1 text-xs font-medium text-red-500 hover:bg-red-50 disabled:opacity-50">
                        Eliminar
                      </button>
                    </div>
                  </td>
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
        <BovineFormModal
          farmId={farmId}
          landPlots={landPlots}
          paddocks={paddocks}
          existing={editing}
          onSuccess={handleSuccess}
          onClose={() => { setShowModal(false); setEditing(undefined); }}
        />
      )}

      <ConfirmDialog
        open={!!toDelete}
        title="Eliminar bovino"
        message={`¿Eliminar el bovino "${toDelete?.identification_number}"? Se marcará como retirado y dejará de aparecer en el hato.`}
        confirmLabel="Eliminar"
        loading={actionLoading !== null}
        onConfirm={handleDelete}
        onCancel={() => setToDelete(null)}
      />
    </div>
  );
}
