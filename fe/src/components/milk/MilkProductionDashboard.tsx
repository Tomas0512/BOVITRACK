import { useEffect, useMemo, useState } from "react";
import { Droplets, Plus, Pencil, Trash2, Download, RefreshCw, Milk, CalendarClock, Timer, Users } from "lucide-react";
import {
  listMilkProduction,
  deleteMilkProduction,
  getMilkSummary,
  type MilkProductionResponse,
  type MilkSummary,
  type MilkListParams,
} from "../../api/milk_production";
import { listBovines, type BovineResponse } from "../../api/bovines";
import { listLandPlots, type LandPlotResponse } from "../../api/land_plots";
import { getApiErrorMessage } from "../../api/errors";
import { useTable } from "../../hooks/useTable";
import Pagination from "../Pagination";
import ConfirmDialog from "../ConfirmDialog";
import MilkProductionFormModal from "./MilkProductionFormModal";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  AreaChart,
  Area,
} from "recharts";

interface Props {
  farmId: string;
}

const MILKING_TYPE_LABELS: Record<string, string> = {
  manual: "Manual",
  mecanico: "Mecánico",
};

const SESSION_LABELS: Record<string, string> = {
  "mañana": "Mañana",
  "tarde": "Tarde",
  "noche": "Noche",
  "sin_sesión": "Sin sesión",
};

const PIE_COLORS = ["#b3541e", "#3a7d44", "#2b6cb0", "#d69e2e", "#805ad5"];

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString("es-CO", { day: "2-digit", month: "2-digit", year: "numeric" });
}

function groupByDay(records: MilkProductionResponse[]) {
  const map = new Map<string, number>();
  for (const r of records) {
    const day = new Date(r.milking_date).toLocaleDateString("es-CO", { day: "2-digit", month: "2-digit", year: "numeric" });
    map.set(day, (map.get(day) ?? 0) + Number(r.quantity_liters));
  }
  return Array.from(map.entries())
    .map(([day, litros]) => ({ day, litros: Number(litros.toFixed(1)) }))
    .sort((a, b) => {
      const [ad, am, ay] = a.day.split("/").map(Number);
      const [bd, bm, by] = b.day.split("/").map(Number);
      return ay - by || am - bm || ad - bd;
    });
}

export default function MilkProductionDashboard({ farmId }: Props) {
  const [records, setRecords] = useState<MilkProductionResponse[]>([]);
  const [bovines, setBovines] = useState<BovineResponse[]>([]);
  const [landPlots, setLandPlots] = useState<LandPlotResponse[]>([]);
  const [summary, setSummary] = useState<MilkSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [bovineFilter, setBovineFilter] = useState("");
  const [sessionFilter, setSessionFilter] = useState("");
  const [typeFilter, setTypeFilter] = useState("");

  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState<MilkProductionResponse | null>(null);
  const [deleting, setDeleting] = useState<MilkProductionResponse | null>(null);
  const [deleteError, setDeleteError] = useState("");

  const bovineName = useMemo(() => {
    const map = new Map(bovines.map((b) => [b.id, `${b.identification_number} · ${b.name ?? "Sin nombre"}`]));
    map.set("", "Todos");
    return map;
  }, [bovines]);

  const loadAll = async (params: MilkListParams = {}) => {
    setLoading(true);
    setError("");
    try {
      const [recordsData, bovinesData, landPlotsData, summaryData] = await Promise.all([
        listMilkProduction(farmId, params),
        listBovines(farmId),
        listLandPlots(farmId, true),
        getMilkSummary(farmId, params.date_from, params.date_to),
      ]);
      setRecords(recordsData);
      setBovines(bovinesData);
      setLandPlots(landPlotsData);
      setSummary(summaryData);
    } catch (err: unknown) {
      setError(getApiErrorMessage(err, "No se pudo cargar la producción de leche"));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAll();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [farmId]);

  const applyFilters = () => {
    loadAll({
      date_from: dateFrom || undefined,
      date_to: dateTo || undefined,
      bovine_id: bovineFilter || undefined,
      milking_session: sessionFilter || undefined,
      milking_type: typeFilter || undefined,
    });
  };

  const clearFilters = () => {
    setDateFrom("");
    setDateTo("");
    setBovineFilter("");
    setSessionFilter("");
    setTypeFilter("");
    loadAll();
  };

  const getValue = (r: MilkProductionResponse, key: string): string | number => {
    const v = (r as unknown as Record<string, unknown>)[key];
    return typeof v === "number" ? v : String(v ?? "");
  };

  const { page, pageCount, start, end, total, paginated, setPage } =
    useTable<MilkProductionResponse>(records, { getValue, initialKey: "milking_date", initialDir: "desc" });

  const daily = useMemo(() => groupByDay(records), [records]);

  const bySession = useMemo(() => {
    const map: Record<string, number> = {};
    for (const kv of Object.entries(summary?.by_session ?? {})) map[SESSION_LABELS[kv[0]] ?? kv[0]] = Number(kv[1]);
    return Object.entries(map).map(([sesion, litros]) => ({ sesion, litros: Number(litros.toFixed(1)) }));
  }, [summary]);

  const byType = useMemo(() => {
    const map: Record<string, number> = {};
    for (const kv of Object.entries(summary?.by_type ?? {})) map[MILKING_TYPE_LABELS[kv[0]] ?? kv[0]] = Number(kv[1]);
    return Object.entries(map).map(([tipo, litros]) => ({ tipo, litros: Number(litros.toFixed(1)) }));
  }, [summary]);

  const topBovines = useMemo(
    () =>
      (summary?.top_bovines ?? [])
        .map((t) => ({
          bovino: bovineName.get(t.bovine_id) ?? "Desconocido",
          litros: Number(t.total_liters),
        }))
        .sort((a, b) => b.litros - a.litros)
        .slice(0, 8),
    [summary, bovineName]
  );

  const todayLitros = useMemo(() => {
    const today = new Date().toDateString();
    return records.filter((r) => new Date(r.milking_date).toDateString() === today)
      .reduce((sum, r) => sum + Number(r.quantity_liters), 0);
  }, [records]);

  const exportCsv = () => {
    const header = "Fecha;Sesión;Tipo;Litros;Bovino;Observaciones";
    const body = records
      .map((r) => {
        const bovino = r.bovine_id ? (bovineName.get(r.bovine_id) ?? "") : "";
        const fields = [formatDate(r.milking_date), SESSION_LABELS[r.milking_session ?? "sin_sesión"] ?? r.milking_session ?? "", MILKING_TYPE_LABELS[r.milking_type] ?? r.milking_type, String(r.quantity_liters), bovino, r.observations ?? ""];
        return fields.map((f) => `"${f.replace(/"/g, '""')}"`).join(";");
      })
      .join("\n");
    const blob = new Blob([`\uFEFF${header}\n${body}`], { type: "text/csv;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `produccion_leche_${new Date().toISOString().slice(0, 10)}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleDelete = async () => {
    if (!deleting) return;
    setDeleteError("");
    try {
      await deleteMilkProduction(farmId, deleting.id);
      setDeleting(null);
      applyFilters();
    } catch (err: unknown) {
      setDeleteError(getApiErrorMessage(err, "No se pudo eliminar el ordeño"));
    }
  };

  return (
    <div className="space-y-6">
      {error && (
        <div className="rounded-lg bg-red-50 px-4 py-2 text-sm text-red-700">{error}</div>
      )}

      <div className="rounded-2xl bg-surface p-6 shadow-sm">
        <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
          <h2 className="text-lg font-bold text-text-primary">
            <Droplets size={20} className="inline mr-1.5 align-text-bottom text-blue-600" />
            Producción de leche
          </h2>
          <div className="flex flex-wrap gap-2">
            <button onClick={() => loadAll()} className="inline-flex items-center gap-1.5 rounded-lg border border-border px-3 py-2 text-sm font-medium text-text-secondary hover:bg-surface-alt">
              <RefreshCw size={15} /> Actualizar
            </button>
            <button onClick={exportCsv} disabled={records.length === 0}
              className="inline-flex items-center gap-1.5 rounded-lg border border-border px-3 py-2 text-sm font-medium text-text-secondary hover:bg-surface-alt disabled:opacity-40">
              <Download size={15} /> Exportar CSV
            </button>
            <button onClick={() => { setEditing(null); setShowForm(true); }}
              className="inline-flex items-center gap-1.5 rounded-lg bg-primary px-3 py-2 text-sm font-bold text-white hover:bg-primary-light">
              <Plus size={15} /> Registrar ordeño
            </button>
          </div>
        </div>

        {/* KPIs */}
        <div className="mb-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <div className="rounded-xl border border-border bg-gradient-to-br from-blue-50 to-transparent p-4">
            <p className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-text-muted"><Milk size={13} className="text-blue-600" />Litros totales</p>
            <p className="mt-1 text-2xl font-bold text-text-primary">{Number(summary?.total_liters ?? 0).toFixed(1)} <span className="text-sm font-medium text-text-muted">L</span></p>
            <p className="text-xs text-text-muted">{summary?.total_records ?? 0} ordeños · {summary?.milking_days ?? 0} días</p>
          </div>
          <div className="rounded-xl border border-border bg-gradient-to-br from-green-50 to-transparent p-4">
            <p className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-text-muted"><CalendarClock size={13} className="text-green-600" />Promedio por día</p>
            <p className="mt-1 text-2xl font-bold text-text-primary">{Number(summary?.avg_daily_liters ?? 0).toFixed(1)} <span className="text-sm font-medium text-text-muted">L/día</span></p>
          </div>
          <div className="rounded-xl border border-border bg-gradient-to-br from-sky-50 to-transparent p-4">
            <p className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-text-muted"><Timer size={13} className="text-sky-600" />Hoy</p>
            <p className="mt-1 text-2xl font-bold text-text-primary">{todayLitros.toFixed(1)} <span className="text-sm font-medium text-text-muted">L</span></p>
          </div>
          <div className="rounded-xl border border-border bg-gradient-to-br from-amber-50 to-transparent p-4">
            <p className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-text-muted"><Users size={13} className="text-amber-600" />Bovinos en ordeño</p>
            <p className="mt-1 text-2xl font-bold text-text-primary">{topBovines.length}</p>
            <p className="text-xs text-text-muted">Top productores del periodo</p>
          </div>
        </div>

        {/* Filtros */}
        <div className="mb-6 grid gap-3 rounded-xl border border-border bg-surface-alt/50 p-4 sm:grid-cols-2 lg:grid-cols-5">
          <div>
            <label className="mb-1 block text-xs font-semibold text-text-secondary">Desde</label>
            <input type="date" value={dateFrom} onChange={(e) => setDateFrom(e.target.value)}
              className="w-full rounded-lg border border-border bg-surface px-3 py-2 text-sm focus:border-primary focus:outline-none" />
          </div>
          <div>
            <label className="mb-1 block text-xs font-semibold text-text-secondary">Hasta</label>
            <input type="date" value={dateTo} onChange={(e) => setDateTo(e.target.value)}
              className="w-full rounded-lg border border-border bg-surface px-3 py-2 text-sm focus:border-primary focus:outline-none" />
          </div>
          <div>
            <label className="mb-1 block text-xs font-semibold text-text-secondary">Bovino</label>
            <select value={bovineFilter} onChange={(e) => setBovineFilter(e.target.value)}
              className="w-full rounded-lg border border-border bg-surface px-3 py-2 text-sm focus:border-primary focus:outline-none">
              <option value="">Todos</option>
              {bovines.filter((b) => b.is_active).map((b) => (
                <option key={b.id} value={b.id}>{b.identification_number} · {b.name ?? "Sin nombre"}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="mb-1 block text-xs font-semibold text-text-secondary">Sesión</label>
            <select value={sessionFilter} onChange={(e) => setSessionFilter(e.target.value)}
              className="w-full rounded-lg border border-border bg-surface px-3 py-2 text-sm focus:border-primary focus:outline-none">
              <option value="">Todas</option>
              {Object.entries(SESSION_LABELS).filter(([v]) => v !== "sin_sesión").map(([v, l]) => (
                <option key={v} value={v}>{l}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="mb-1 block text-xs font-semibold text-text-secondary">Tipo</label>
            <select value={typeFilter} onChange={(e) => setTypeFilter(e.target.value)}
              className="w-full rounded-lg border border-border bg-surface px-3 py-2 text-sm focus:border-primary focus:outline-none">
              <option value="">Todos</option>
              {Object.entries(MILKING_TYPE_LABELS).map(([v, l]) => (
                <option key={v} value={v}>{l}</option>
              ))}
            </select>
          </div>
          <div className="flex items-end gap-2 lg:col-span-5">
            <button onClick={applyFilters}
              className="rounded-lg bg-primary px-4 py-2 text-sm font-bold text-white hover:bg-primary-light">
              Aplicar filtros
            </button>
            <button onClick={clearFilters}
              className="rounded-lg border border-border px-4 py-2 text-sm font-medium text-text-secondary hover:bg-surface-alt">
              Limpiar
            </button>
          </div>
        </div>

        {/* Gráficas */}
        <div className="grid gap-4 lg:grid-cols-2">
          <div className="rounded-xl border border-border p-4">
            <h3 className="mb-3 text-sm font-bold text-text-secondary">Producción por día</h3>
            {daily.length === 0 ? (
              <p className="py-8 text-center text-sm text-text-muted">Sin datos en el periodo.</p>
            ) : (
              <ResponsiveContainer width="100%" height={220}>
                <AreaChart data={daily} margin={{ top: 4, right: 8, bottom: 4, left: 0 }}>
                  <defs>
                    <linearGradient id="milkFill" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#2b6cb0" stopOpacity={0.35} />
                      <stop offset="95%" stopColor="#2b6cb0" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#eae5d9" />
                  <XAxis dataKey="day" tick={{ fontSize: 10, fill: "#9c8e7b" }} tickLine={false} axisLine={false} />
                  <YAxis tick={{ fontSize: 11, fill: "#9c8e7b" }} tickLine={false} axisLine={false} unit=" L" width={55} />
                  <Tooltip formatter={(v) => [`${Number(v).toFixed(1)} L`, "Producción"]} labelStyle={{ fontSize: 12 }} />
                  <Area type="monotone" dataKey="litros" stroke="#2b6cb0" strokeWidth={2.5} fill="url(#milkFill)" name="Producción" />
                </AreaChart>
              </ResponsiveContainer>
            )}
          </div>

          <div className="rounded-xl border border-border p-4">
            <h3 className="mb-3 text-sm font-bold text-text-secondary">Por sesión</h3>
            {bySession.length === 0 ? (
              <p className="py-8 text-center text-sm text-text-muted">Sin datos en el periodo.</p>
            ) : (
              <ResponsiveContainer width="100%" height={220}>
                <PieChart>
                  <Pie data={bySession} dataKey="litros" nameKey="sesion" cx="50%" cy="50%" outerRadius={80}
                    labelLine={false}
                    label={(entry) => {
                      const p = entry as unknown as { sesion?: string; percent?: number };
                      return `${p.sesion ?? ""} ${Math.round((p.percent ?? 0) * 100)}%`;
                    }}>
                    {bySession.map((_, i) => <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />)}
                  </Pie>
                  <Tooltip formatter={(v) => [`${Number(v).toFixed(1)} L`, "Litros"]} />
                </PieChart>
              </ResponsiveContainer>
            )}
          </div>

          <div className="rounded-xl border border-border p-4">
            <h3 className="mb-3 text-sm font-bold text-text-secondary">Top bovinos productores</h3>
            {topBovines.length === 0 ? (
              <p className="py-8 text-center text-sm text-text-muted">Sin datos en el periodo.</p>
            ) : (
              <ResponsiveContainer width="100%" height={220}>
                <BarChart data={topBovines} layout="vertical" margin={{ top: 4, right: 24, bottom: 4, left: 8 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#eae5d9" />
                  <XAxis type="number" tick={{ fontSize: 11, fill: "#9c8e7b" }} tickLine={false} axisLine={false} unit=" L" />
                  <YAxis type="category" dataKey="bovino" width={150} tick={{ fontSize: 10, fill: "#9c8e7b" }} tickLine={false} axisLine={false} />
                  <Tooltip formatter={(v) => [`${Number(v).toFixed(1)} L`, "Litros"]} />
                  <Bar dataKey="litros" fill="#b3541e" radius={[0, 4, 4, 0]} barSize={14} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>

          <div className="rounded-xl border border-border p-4">
            <h3 className="mb-3 text-sm font-bold text-text-secondary">Manual vs Mecánico</h3>
            {byType.length === 0 ? (
              <p className="py-8 text-center text-sm text-text-muted">Sin datos en el periodo.</p>
            ) : (
              <ResponsiveContainer width="100%" height={220}>
                <BarChart data={byType} margin={{ top: 4, right: 16, bottom: 4, left: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#eae5d9" />
                  <XAxis dataKey="tipo" tick={{ fontSize: 12, fill: "#9c8e7b" }} tickLine={false} axisLine={false} />
                  <YAxis tick={{ fontSize: 11, fill: "#9c8e7b" }} tickLine={false} axisLine={false} unit=" L" width={55} />
                  <Tooltip formatter={(v) => [`${Number(v).toFixed(1)} L`, "Litros"]} />
                  <Bar dataKey="litros" fill="#3a7d44" radius={[4, 4, 0, 0]} barSize={40} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>
      </div>

      {/* Tabla de registros */}
      <div className="rounded-2xl bg-surface p-6 shadow-sm">
        <div className="mb-4 flex items-center justify-between">
          <h3 className="font-bold text-text-primary">
            <Droplets size={18} className="inline mr-1.5 align-text-bottom text-blue-600" />
            Registros de ordeño
          </h3>
          <span className="rounded-full bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-700">
            Total: {Number(summary?.total_liters ?? 0).toFixed(1)} L ({records.length} registros)
          </span>
        </div>

        {loading && (
          <div className="flex justify-center py-8">
            <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
          </div>
        )}
        {!loading && records.length === 0 && (
          <p className="py-6 text-center text-sm text-text-muted">
            Sin registros. Usa "Registrar ordeño" para empezar el control de producción.
          </p>
        )}
        {!loading && records.length > 0 && (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[680px] text-left text-sm">
              <thead>
                <tr className="border-b border-border text-xs font-semibold uppercase tracking-wide text-text-muted">
                  <th className="pb-2 pr-4">Fecha</th>
                  <th className="pb-2 pr-4">Sesión</th>
                  <th className="pb-2 pr-4">Tipo</th>
                  <th className="pb-2 pr-4">Litros</th>
                  <th className="pb-2 pr-4">Bovino</th>
                  <th className="pb-2 pr-4">Observaciones</th>
                  <th className="pb-2 text-right">Acciones</th>
                </tr>
              </thead>
              <tbody>
                {paginated.map((r) => (
                  <tr key={r.id} className="border-b border-border last:border-0 hover:bg-surface-alt">
                    <td className="py-2 pr-4 font-medium text-text-primary whitespace-nowrap">
                      {formatDate(r.milking_date)}
                    </td>
                    <td className="py-2 pr-4">
                      {r.milking_session ? (
                        <span className="rounded-full bg-sky-50 px-2 py-0.5 text-xs font-medium text-sky-700">
                          {SESSION_LABELS[r.milking_session] ?? r.milking_session}
                        </span>
                      ) : (
                        <span className="text-text-muted">—</span>
                      )}
                    </td>
                    <td className="py-2 pr-4 text-text-secondary">
                      {MILKING_TYPE_LABELS[r.milking_type] ?? r.milking_type}
                    </td>
                    <td className="py-2 pr-4 font-semibold text-blue-700">
                      {Number(r.quantity_liters).toFixed(1)} L
                    </td>
                    <td className="py-2 pr-4 text-text-secondary">
                      {r.bovine_id ? (bovineName.get(r.bovine_id) ?? "—") : <span className="text-text-muted">Lote</span>}
                    </td>
                    <td className="max-w-[220px] truncate py-2 pr-4 text-text-secondary">
                      {r.observations ?? <span className="text-text-muted">—</span>}
                    </td>
                    <td className="py-2">
                      <div className="flex justify-end gap-1">
                        <button onClick={() => { setEditing(r); setShowForm(true); }} aria-label="Editar"
                          className="rounded-lg p-1.5 text-text-muted hover:bg-blue-50 hover:text-blue-700">
                          <Pencil size={15} />
                        </button>
                        <button onClick={() => setDeleting(r)} aria-label="Eliminar"
                          className="rounded-lg p-1.5 text-text-muted hover:bg-red-50 hover:text-red-600">
                          <Trash2 size={15} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            <div className="mt-4">
              <Pagination page={page} pageCount={pageCount} start={start} end={end} total={total} onChange={(p) => setPage(p)} />
            </div>
          </div>
        )}
      </div>

      {showForm && (
        <MilkProductionFormModal
          farmId={farmId}
          bovines={bovines}
          landPlots={landPlots}
          existing={editing ?? undefined}
          onSuccess={() => { setShowForm(false); setEditing(null); applyFilters(); }}
          onClose={() => { setShowForm(false); setEditing(null); }}
        />
      )}

      <ConfirmDialog
        open={Boolean(deleting)}
        title="Eliminar ordeño"
        message={`¿Eliminar el ordeño de ${deleting ? formatDate(deleting.milking_date) : ""} (${deleting ? Number(deleting.quantity_liters).toFixed(1) : ""} L)? Esta acción es permanente.`}
        confirmLabel="Eliminar"
        onConfirm={handleDelete}
        onCancel={() => { setDeleting(null); setDeleteError(""); }}
      >
        {deleteError && <p className="mb-3 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{deleteError}</p>}
      </ConfirmDialog>
    </div>
  );
}