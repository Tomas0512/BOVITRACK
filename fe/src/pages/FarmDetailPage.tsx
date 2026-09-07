import { useEffect, useState } from "react";
import { useParams, Link, useSearchParams } from "react-router-dom";
import { AlertTriangle } from "lucide-react";
import { getFarm, type FarmResponse } from "../api/farms";
import EmployeeList from "../components/employees/EmployeeList";
import LandPlotList from "../components/land_plots/LandPlotList";
import PaddockList from "../components/paddocks/PaddockList";
import BovineList from "../components/bovines/BovineList";
import SanitaryPlanList from "../components/bovines/SanitaryPlanList";
import FarmTreatments from "../components/bovines/FarmTreatments";
import FoodList from "../components/food/FoodList";
import AuditLogList from "../components/audit/AuditLogList";
import AlertBanner from "../components/layout/AlertBanner";
import MovementList from "../components/movements/MovementList";
import DocumentManager from "../components/documents/DocumentManager";
import CalfList from "../components/calves/CalfList";
import MilkProductionDashboard from "../components/milk/MilkProductionDashboard";

export default function FarmDetailPage() {
  const { farmId } = useParams<{ farmId: string }>();
  const [searchParams] = useSearchParams();
  const activeTab = searchParams.get("tab") ?? "bovinos";
  const [farm, setFarm] = useState<FarmResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

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
      case "sanidad": return (
        <div className="space-y-6">
          <SanitaryPlanList farmId={farm.id} />
          <FarmTreatments farmId={farm.id} />
        </div>
      );
      case "alimentacion": return <FoodList farmId={farm.id} />;
      case "produccion": return <MilkProductionDashboard farmId={farm.id} />;
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
      default: return <BovineList farmId={farm.id} />;
    }
  };

  return (
    <div>
      {/* Módulo activo */}
      {renderTab()}

      {/* Resumen de la finca */}
      <div className="mt-6 space-y-4">
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
      </div>
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
