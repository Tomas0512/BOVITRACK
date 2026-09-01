import { useEffect, useState, type ReactNode } from "react";
import { useParams, Link, useNavigate, useSearchParams } from "react-router-dom";
import {
  AlertTriangle,
  Tractor,
  BarChart3,
  FileText,
  Bell,
  LayoutDashboard,
  Beef,
  Sprout,
  Pill,
  Wheat,
  ArrowLeftRight,
  Map,
  Users,
  ShieldCheck,
} from "lucide-react";
import { getFarm, updateFarm, deleteFarm, listDepartments, listPurposes, type FarmResponse, type FarmRequest, type DepartmentOption, type PurposeOption } from "../api/farms";
import EmployeeList from "../components/employees/EmployeeList";
import LandPlotList from "../components/land_plots/LandPlotList";
import PaddockList from "../components/paddocks/PaddockList";
import BovineList from "../components/bovines/BovineList";
import SanitaryPlanList from "../components/bovines/SanitaryPlanList";
import FoodList from "../components/food/FoodList";
import AuditLogList from "../components/audit/AuditLogList";
import AlertBanner from "../components/layout/AlertBanner";
import MovementList from "../components/movements/MovementList";
import DocumentManager from "../components/documents/DocumentManager";
import CalfList from "../components/calves/CalfList";

interface TabDef {
  id: string;
  label: string;
  icon: ReactNode;
}

const TABS: TabDef[] = [
  { id: "resumen", label: "Resumen", icon: <LayoutDashboard size={18} /> },
  { id: "bovinos", label: "Ganado", icon: <Beef size={18} /> },
  { id: "terneros", label: "Terneros", icon: <Sprout size={18} /> },
  { id: "sanidad", label: "Sanidad", icon: <Pill size={18} /> },
  { id: "alimentacion", label: "Alimentación", icon: <Wheat size={18} /> },
  { id: "movimientos", label: "Movimientos", icon: <ArrowLeftRight size={18} /> },
  { id: "lotes", label: "Lotes y Potreros", icon: <Map size={18} /> },
  { id: "documentos", label: "Documentos", icon: <FileText size={18} /> },
  { id: "empleados", label: "Empleados", icon: <Users size={18} /> },
  { id: "auditoria", label: "Auditoría", icon: <ShieldCheck size={18} /> },
];

export default function FarmDetailPage() {
  const { farmId } = useParams<{ farmId: string }>();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const activeTab = searchParams.get("tab") ?? "resumen";
  const [farm, setFarm] = useState<FarmResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [editing, setEditing] = useState(false);
  const [editStep, setEditStep] = useState(0);
  const [departments, setDepartments] = useState<DepartmentOption[]>([]);
  const [purposes, setPurposes] = useState<PurposeOption[]>([]);
  const [editForm, setEditForm] = useState<FarmRequest | null>(null);
  const [saving, setSaving] = useState(false);

  const setTab = (id: string) => setSearchParams({ tab: id });

  const nextEditStep = () => setEditStep((s) => Math.min(s + 1, 1));
  const prevEditStep = () => setEditStep((s) => Math.max(s - 1, 0));

  const loadFarm = async () => {
    if (!farmId) return;
    try {
      const data = await getFarm(farmId);
      setFarm(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al cargar la finca");
    } finally {
      setLoading(false);
    }
  };

  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => { loadFarm(); }, [farmId]);

  const handleEdit = async () => {
    if (!farm) return;
    const [deps, purps] = await Promise.all([listDepartments(), listPurposes()]);
    setDepartments(deps);
    setPurposes(purps);
    setEditForm({
      name: farm.name,
      address: farm.address,
      department_id: farm.department_id,
      city_municipality: farm.city_municipality,
      total_area: farm.total_area,
      area_unit: farm.area_unit,
      purpose_id: farm.purpose_id,
      farm_identifier: farm.farm_identifier,
      phone: farm.phone,
    });
    setEditStep(0);
    setEditing(true);
  };

  const handleSaveEdit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!farmId || !editForm) return;
    setSaving(true);
    try {
      const updated = await updateFarm(farmId, editForm);
      setFarm(updated);
      setEditing(false);
    } catch {
      setError("No se pudo actualizar la finca");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!farmId || !confirm("¿Estás seguro de eliminar esta finca? Esta acción la desactivará.")) return;
    try {
      await deleteFarm(farmId);
      navigate("/dashboard");
    } catch {
      setError("No se pudo eliminar la finca");
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  if (error || !farm) {
    return (
      <div className="flex justify-center pt-12">
        <div className="w-full max-w-md rounded-2xl bg-surface p-8 text-center shadow-lg">
          <div className="mb-3" aria-hidden="true"><AlertTriangle size={40} className="text-amber-500 mx-auto" /></div>
          <h2 className="mb-2 text-lg font-bold text-text-primary">Finca no encontrada</h2>
          <p className="mb-6 text-sm text-text-secondary">{error || "No se pudo cargar la finca."}</p>
          <Link
            to="/dashboard"
            className="inline-block rounded-lg bg-primary px-6 py-2.5 text-sm font-bold text-white no-underline transition-colors hover:bg-primary-light"
          >
            Volver al dashboard
          </Link>
        </div>
      </div>
    );
  }

  const renderTab = () => {
    switch (activeTab) {
      case "bovinos": return <BovineList farmId={farm.id} />;
      case "terneros": return <CalfList farmId={farm.id} />;
      case "sanidad": return <SanitaryPlanList farmId={farm.id} />;
      case "alimentacion": return <FoodList farmId={farm.id} />;
      case "movimientos": return <MovementList farmId={farm.id} />;
      case "lotes": return (
        <div className="space-y-6">
          <LandPlotList farmId={farm.id} />
          <PaddockList farmId={farm.id} />
        </div>
      );
      case "documentos": return <DocumentManager farmId={farm.id} />;
      case "empleados": return <EmployeeList farmId={farm.id} />;
      case "auditoria": return <AuditLogList farmId={farm.id} />;
      default: return (
        <>
          <div className="grid gap-4 sm:grid-cols-2">
            <InfoCard label="Dirección" value={farm.address} />
            <InfoCard label="Ciudad o municipio" value={farm.city_municipality} />
            <InfoCard label="Área total" value={`${farm.total_area} ${farm.area_unit}`} />
            <InfoCard label="Teléfono" value={farm.phone ?? "No registrado"} />
            <InfoCard label="Estado" value={farm.is_active ? "Activa" : "Inactiva"} />
            <InfoCard label="Fecha de creación" value={new Date(farm.created_at).toLocaleDateString("es-CO")} />
            <InfoCard label="Última actualización" value={new Date(farm.updated_at).toLocaleDateString("es-CO")} />
          </div>
          <AlertBanner farmId={farm.id} />
        </>
      );
    }
  };

  return (
    <div>
      {/* Farm header */}
      <div className="mb-6 rounded-2xl bg-surface p-6 shadow-sm">
        <div className="mb-4 flex items-center gap-3">
          <Tractor size={36} className="text-primary shrink-0" />
          <div>
            <h1 className="text-2xl font-bold text-text-primary">{farm.name}</h1>
            <p className="text-sm text-text-secondary">ID: {farm.farm_identifier}</p>
          </div>
          <div className="ml-auto flex flex-wrap gap-2">
            <Link to={`/farms/${farmId}/economics`}
              className="inline-flex items-center gap-1.5 rounded-lg border border-border px-4 py-2 text-sm font-medium text-text-secondary no-underline hover:bg-surface-alt">
              <BarChart3 size={16} />
              Económico
            </Link>
            <Link to={`/farms/${farmId}/reports`}
              className="inline-flex items-center gap-1.5 rounded-lg border border-border px-4 py-2 text-sm font-medium text-text-secondary no-underline hover:bg-surface-alt">
              <FileText size={16} />
              Reportes
            </Link>
            <Link to={`/farms/${farmId}/alerts`}
              className="inline-flex items-center gap-1.5 rounded-lg border border-border px-4 py-2 text-sm font-medium text-text-secondary no-underline hover:bg-surface-alt">
              <Bell size={16} />
              Alertas
            </Link>
            <button onClick={handleEdit}
              className="rounded-lg border border-border px-4 py-2 text-sm font-medium text-text-secondary hover:bg-surface-alt">
              Editar
            </button>
            <button onClick={handleDelete}
              className="rounded-lg border border-red-200 px-4 py-2 text-sm font-medium text-red-600 hover:bg-red-50">
              Eliminar
            </button>
          </div>
        </div>

        {/* Edit form (collapsible) */}
        {editing && editForm && (
          <form onSubmit={handleSaveEdit} className="rounded-xl border border-border bg-surface p-4">
            <h3 className="mb-3 text-sm font-bold text-text-secondary">Editar finca</h3>
            <div className="mb-4 flex items-center gap-1.5">
              {["Ubicación", "Área y ID"].map((label, i) => (
                <button key={i} type="button" onClick={() => { if (i < editStep) setEditStep(i); }} disabled={i > editStep}
                  className={`flex-1 rounded-lg px-2 py-1.5 text-center text-xs font-semibold transition-colors ${i === editStep ? "bg-primary text-white" : i < editStep ? "bg-green-100 text-green-700" : "bg-surface-alt text-text-muted cursor-default"}`}
                >
                  {i < editStep ? "✓ " : ""}{label}
                </button>
              ))}
            </div>
            {editStep === 0 && (
              <div className="grid gap-3 sm:grid-cols-2">
                <div>
                  <label className="mb-1 block text-xs font-medium text-text-secondary">Nombre</label>
                  <input type="text" value={editForm.name} onChange={(e) => setEditForm({ ...editForm, name: e.target.value })}
                    className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none" required />
                </div>
                <div>
                  <label className="mb-1 block text-xs font-medium text-text-secondary">Dirección</label>
                  <input type="text" value={editForm.address} onChange={(e) => setEditForm({ ...editForm, address: e.target.value })}
                    className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none" required />
                </div>
                <div>
                  <label className="mb-1 block text-xs font-medium text-text-secondary">Departamento</label>
                  <select value={editForm.department_id} onChange={(e) => setEditForm({ ...editForm, department_id: e.target.value })}
                    className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none">
                    {departments.map((d) => <option key={d.id} value={d.id}>{d.name}</option>)}
                  </select>
                </div>
                <div>
                  <label className="mb-1 block text-xs font-medium text-text-secondary">Ciudad / Municipio</label>
                  <input type="text" value={editForm.city_municipality} onChange={(e) => setEditForm({ ...editForm, city_municipality: e.target.value })}
                    className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none" required />
                </div>
              </div>
            )}
            {editStep === 1 && (
              <div className="grid gap-3 sm:grid-cols-2">
                <div>
                  <label className="mb-1 block text-xs font-medium text-text-secondary">Área total</label>
                  <input type="number" min={0.01} step={0.01} value={editForm.total_area}
                    onChange={(e) => setEditForm({ ...editForm, total_area: parseFloat(e.target.value) })}
                    className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none" required />
                </div>
                <div>
                  <label className="mb-1 block text-xs font-medium text-text-secondary">Propósito</label>
                  <select value={editForm.purpose_id} onChange={(e) => setEditForm({ ...editForm, purpose_id: e.target.value })}
                    className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none">
                    {purposes.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
                  </select>
                </div>
                <div>
                  <label className="mb-1 block text-xs font-medium text-text-secondary">Identificador</label>
                  <input type="text" value={editForm.farm_identifier} onChange={(e) => setEditForm({ ...editForm, farm_identifier: e.target.value })}
                    className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none" required />
                </div>
                <div>
                  <label className="mb-1 block text-xs font-medium text-text-secondary">Teléfono</label>
                  <input type="text" value={editForm.phone ?? ""} onChange={(e) => setEditForm({ ...editForm, phone: e.target.value || null })}
                    className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none" />
                </div>
              </div>
            )}
            <div className="mt-3 flex gap-2">
              {editStep > 0 && (
                <button type="button" onClick={prevEditStep}
                  className="rounded-lg border border-border px-4 py-2 text-sm font-medium text-text-secondary hover:bg-surface-alt">
                  ← Anterior
                </button>
              )}
              {editStep < 1 ? (
                <button type="button" onClick={nextEditStep}
                  className="rounded-lg bg-primary px-4 py-2 text-sm font-bold text-white hover:bg-primary-light">
                  Siguiente →
                </button>
              ) : (
                <>
                  <button type="button" onClick={() => setEditing(false)}
                    className="rounded-lg border border-border px-4 py-2 text-sm font-medium text-text-secondary hover:bg-surface-alt">
                    Cancelar
                  </button>
                  <button type="submit" disabled={saving}
                    className="rounded-lg bg-primary px-4 py-2 text-sm font-bold text-white hover:bg-primary-light disabled:opacity-60">
                    {saving ? "Guardando..." : "Guardar cambios"}
                  </button>
                </>
              )}
            </div>
          </form>
        )}
      </div>

      {/* Tabs */}
      <div className="mb-6 flex flex-wrap gap-1.5 border-b border-border pb-2">
        {TABS.map((t) => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={`inline-flex items-center gap-1.5 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
              activeTab === t.id
                ? "bg-primary text-white"
                : "text-text-secondary hover:bg-surface-alt hover:text-text-primary"
            }`}
          >
            <span className={activeTab === t.id ? "" : "text-primary"}>{t.icon}</span>
            {t.label}
          </button>
        ))}
      </div>

      {/* Active tab content */}
      {renderTab()}
    </div>
  );
}

function InfoCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-border bg-surface p-4">
      <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-text-muted">{label}</p>
      <p className="text-sm font-medium text-text-primary">{value}</p>
    </div>
  );
}
