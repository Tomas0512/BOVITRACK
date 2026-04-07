import { useEffect, useState } from "react";
import { listBovines, deleteBovine, type BovineResponse } from "../../api/bovines";
import { listLandPlots, type LandPlotResponse } from "../../api/land_plots";
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
  vendido: "bg-gray-100 text-gray-600",
  muerto: "bg-red-50 text-red-700",
  retirado: "bg-yellow-50 text-yellow-700",
};

export default function BovineList({ farmId }: Props) {
  const [bovines, setBovines] = useState<BovineResponse[]>([]);
  const [landPlots, setLandPlots] = useState<LandPlotResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showModal, setShowModal] = useState(false);
  const [editing, setEditing] = useState<BovineResponse | undefined>();
  const [actionLoading, setActionLoading] = useState<string | null>(null);
  const [filterSex, setFilterSex] = useState("");

  const fetchData = async () => {
    setLoading(true);
    setError("");
    try {
      const [b, lp] = await Promise.all([
        listBovines(farmId, filterSex ? { sex: filterSex } : {}),
        listLandPlots(farmId, true),
      ]);
      setBovines(b);
      setLandPlots(lp);
    } catch {
      setError("No se pudieron cargar los bovinos");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, [farmId, filterSex]);

  const handleDelete = async (b: BovineResponse) => {
    if (!confirm(`¿Eliminar el bovino "${b.identification_number}"?`)) return;
    setActionLoading(b.id);
    try {
      await deleteBovine(farmId, b.id);
      await fetchData();
    } catch {
      setError("No se pudo eliminar el bovino");
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
    <div className="mt-6 rounded-2xl bg-white p-6 shadow-sm">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h2 className="text-lg font-bold text-gray-900">Bovinos</h2>
          <p className="text-xs text-gray-400">{bovines.length} registro{bovines.length !== 1 ? "s" : ""}</p>
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
            className={`rounded-full px-3 py-1 text-xs font-medium transition-colors ${filterSex === f.val ? "bg-primary text-white" : "bg-gray-100 text-gray-600 hover:bg-gray-200"}`}>
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
        <div className="rounded-lg border border-dashed border-gray-200 py-10 text-center">
          <p className="text-sm text-gray-400">No hay bovinos registrados</p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-100 text-left text-xs font-semibold uppercase tracking-wide text-gray-400">
                <th className="pb-2 pr-4">ID</th>
                <th className="pb-2 pr-4">Nombre</th>
                <th className="pb-2 pr-4">Sexo</th>
                <th className="pb-2 pr-4">Raza</th>
                <th className="pb-2 pr-4">Estado</th>
                <th className="pb-2 pr-4">Peso actual</th>
                <th className="pb-2">Acciones</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {bovines.map((b) => (
                <tr key={b.id} className="hover:bg-gray-50">
                  <td className="py-3 pr-4 font-mono text-xs text-gray-600">{b.identification_number}</td>
                  <td className="py-3 pr-4 font-medium text-gray-800">{b.name ?? "—"}</td>
                  <td className="py-3 pr-4">
                    <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${SEX_BADGE[b.sex] ?? "bg-gray-100 text-gray-600"}`}>
                      {b.sex}
                    </span>
                  </td>
                  <td className="py-3 pr-4 text-gray-500">{b.breed ?? "—"}</td>
                  <td className="py-3 pr-4">
                    <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${STATUS_BADGE[b.status] ?? "bg-gray-100 text-gray-600"}`}>
                      {b.status}
                    </span>
                  </td>
                  <td className="py-3 pr-4 text-gray-500">{b.current_weight ? `${b.current_weight} kg` : "—"}</td>
                  <td className="py-3">
                    <div className="flex gap-2">
                      <Link to={`/farms/${farmId}/bovines/${b.id}`}
                        className="rounded px-2 py-1 text-xs font-medium text-primary hover:bg-primary/10 no-underline">
                        Ver
                      </Link>
                      <button onClick={() => { setEditing(b); setShowModal(true); }}
                        className="rounded px-2 py-1 text-xs font-medium text-gray-500 hover:bg-gray-100">
                        Editar
                      </button>
                      <button onClick={() => handleDelete(b)} disabled={actionLoading === b.id}
                        className="rounded px-2 py-1 text-xs font-medium text-red-500 hover:bg-red-50 disabled:opacity-50">
                        Eliminar
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {showModal && (
        <BovineFormModal
          farmId={farmId}
          landPlots={landPlots}
          existing={editing}
          onSuccess={handleSuccess}
          onClose={() => { setShowModal(false); setEditing(undefined); }}
        />
      )}
    </div>
  );
}
