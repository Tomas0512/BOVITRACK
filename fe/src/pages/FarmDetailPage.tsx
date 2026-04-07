import { useEffect, useState } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import { getFarm, updateFarm, deleteFarm, listDepartments, listPurposes, type FarmResponse, type FarmRequest, type DepartmentOption, type PurposeOption } from "../api/farms";
import EmployeeList from "../components/employees/EmployeeList";
import LandPlotList from "../components/land_plots/LandPlotList";
import PaddockList from "../components/paddocks/PaddockList";
import BovineList from "../components/bovines/BovineList";
import AuditLogList from "../components/audit/AuditLogList";

export default function FarmDetailPage() {
  const { farmId } = useParams<{ farmId: string }>();
  const navigate = useNavigate();
  const [farm, setFarm] = useState<FarmResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [editing, setEditing] = useState(false);
  const [departments, setDepartments] = useState<DepartmentOption[]>([]);
  const [purposes, setPurposes] = useState<PurposeOption[]>([]);
  const [editForm, setEditForm] = useState<FarmRequest | null>(null);
  const [saving, setSaving] = useState(false);

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
        <div className="w-full max-w-md rounded-2xl bg-white p-8 text-center shadow-lg">
          <div className="mb-3 text-5xl">⚠️</div>
          <h2 className="mb-2 text-lg font-bold text-gray-800">Finca no encontrada</h2>
          <p className="mb-6 text-sm text-gray-500">{error || "No se pudo cargar la finca."}</p>
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

  return (
    <div>
      <div className="rounded-2xl bg-white p-8 shadow-sm">
        <div className="mb-6 flex items-center gap-3">
          <span className="text-4xl">🐄</span>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{farm.name}</h1>
            <p className="text-sm text-gray-500">ID: {farm.farm_identifier}</p>
          </div>
          <div className="ml-auto flex gap-2">
            <button onClick={handleEdit}
              className="rounded-lg border border-gray-200 px-4 py-2 text-sm font-medium text-gray-600 hover:bg-gray-50">
              Editar
            </button>
            <button onClick={handleDelete}
              className="rounded-lg border border-red-200 px-4 py-2 text-sm font-medium text-red-600 hover:bg-red-50">
              Eliminar
            </button>
          </div>
        </div>

        {editing && editForm && (
          <form onSubmit={handleSaveEdit} className="mb-6 rounded-xl border border-gray-200 bg-surface p-4">
            <h3 className="mb-3 text-sm font-bold text-gray-700">Editar finca</h3>
            <div className="grid gap-3 sm:grid-cols-2">
              <div>
                <label className="mb-1 block text-xs font-medium text-gray-600">Nombre</label>
                <input type="text" value={editForm.name} onChange={(e) => setEditForm({ ...editForm, name: e.target.value })}
                  className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-primary focus:outline-none" required />
              </div>
              <div>
                <label className="mb-1 block text-xs font-medium text-gray-600">Dirección</label>
                <input type="text" value={editForm.address} onChange={(e) => setEditForm({ ...editForm, address: e.target.value })}
                  className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-primary focus:outline-none" required />
              </div>
              <div>
                <label className="mb-1 block text-xs font-medium text-gray-600">Departamento</label>
                <select value={editForm.department_id} onChange={(e) => setEditForm({ ...editForm, department_id: e.target.value })}
                  className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-primary focus:outline-none">
                  {departments.map((d) => <option key={d.id} value={d.id}>{d.name}</option>)}
                </select>
              </div>
              <div>
                <label className="mb-1 block text-xs font-medium text-gray-600">Ciudad / Municipio</label>
                <input type="text" value={editForm.city_municipality} onChange={(e) => setEditForm({ ...editForm, city_municipality: e.target.value })}
                  className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-primary focus:outline-none" required />
              </div>
              <div>
                <label className="mb-1 block text-xs font-medium text-gray-600">Área total</label>
                <input type="number" min={0.01} step={0.01} value={editForm.total_area}
                  onChange={(e) => setEditForm({ ...editForm, total_area: parseFloat(e.target.value) })}
                  className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-primary focus:outline-none" required />
              </div>
              <div>
                <label className="mb-1 block text-xs font-medium text-gray-600">Propósito</label>
                <select value={editForm.purpose_id} onChange={(e) => setEditForm({ ...editForm, purpose_id: e.target.value })}
                  className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-primary focus:outline-none">
                  {purposes.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
                </select>
              </div>
              <div>
                <label className="mb-1 block text-xs font-medium text-gray-600">Identificador</label>
                <input type="text" value={editForm.farm_identifier} onChange={(e) => setEditForm({ ...editForm, farm_identifier: e.target.value })}
                  className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-primary focus:outline-none" required />
              </div>
              <div>
                <label className="mb-1 block text-xs font-medium text-gray-600">Teléfono</label>
                <input type="text" value={editForm.phone ?? ""} onChange={(e) => setEditForm({ ...editForm, phone: e.target.value || null })}
                  className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-primary focus:outline-none" />
              </div>
            </div>
            <div className="mt-3 flex gap-2">
              <button type="button" onClick={() => setEditing(false)}
                className="rounded-lg border border-gray-200 px-4 py-2 text-sm font-medium text-gray-600 hover:bg-gray-50">
                Cancelar
              </button>
              <button type="submit" disabled={saving}
                className="rounded-lg bg-primary px-4 py-2 text-sm font-bold text-white hover:bg-primary-light disabled:opacity-60">
                {saving ? "Guardando..." : "Guardar cambios"}
              </button>
            </div>
          </form>
        )}

        <div className="grid gap-4 sm:grid-cols-2">
          <InfoCard label="Dirección" value={farm.address} />
          <InfoCard label="Ciudad o municipio" value={farm.city_municipality} />
          <InfoCard label="Área total" value={`${farm.total_area} ${farm.area_unit}`} />
          <InfoCard label="Teléfono" value={farm.phone ?? "No registrado"} />
          <InfoCard label="Estado" value={farm.is_active ? "Activa ✅" : "Inactiva ❌"} />
          <InfoCard label="Fecha de creación" value={new Date(farm.created_at).toLocaleDateString("es-CO")} />
          <InfoCard label="Última actualización" value={new Date(farm.updated_at).toLocaleDateString("es-CO")} />
        </div>
      </div>

      <LandPlotList farmId={farm.id} />
      <PaddockList farmId={farm.id} />
      <BovineList farmId={farm.id} />
      <EmployeeList farmId={farm.id} />
      <AuditLogList farmId={farm.id} />
    </div>
  );
}

function InfoCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-gray-100 bg-surface p-4">
      <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-gray-400">{label}</p>
      <p className="text-sm font-medium text-gray-800">{value}</p>
    </div>
  );
}
