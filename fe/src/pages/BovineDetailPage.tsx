import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { FileText, BarChart3, Dna, Syringe, AlertTriangle, ArrowDownToLine, ArrowUpFromLine, Tag, Mars, Venus } from "lucide-react";
import { getBovine, type BovineResponse } from "../api/bovines";
import WeightChart from "../components/bovines/WeightChart";
import WeightHistory from "../components/bovines/WeightHistory";
import MilkProductionList from "../components/bovines/MilkProductionList";
import FoodList from "../components/bovines/FoodList";
import TreatmentList from "../components/bovines/TreatmentList";
import ReproductiveTimeline from "../components/bovines/ReproductiveTimeline";

type Tab = "general" | "productivo" | "reproductivo" | "sanitario";

const TABS: { id: Tab; label: string; icon: React.ReactNode }[] = [
  { id: "general", label: "General", icon: <FileText size={16} /> },
  { id: "productivo", label: "Productivo", icon: <BarChart3 size={16} /> },
  { id: "reproductivo", label: "Reproductivo", icon: <Dna size={16} /> },
  { id: "sanitario", label: "Sanitario", icon: <Syringe size={16} /> },
];

export default function BovineDetailPage() {
  const { farmId, bovineId } = useParams<{ farmId: string; bovineId: string }>();
  const [bovine, setBovine] = useState<BovineResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [activeTab, setActiveTab] = useState<Tab>("general");

  useEffect(() => {
    if (!farmId || !bovineId) return;
    getBovine(farmId, bovineId)
      .then(setBovine)
      .catch(() => setError("No se pudo cargar el bovino"))
      .finally(() => setLoading(false));
  }, [farmId, bovineId]);

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  if (error || !bovine) {
    return (
      <div className="flex justify-center pt-12">
        <div className="w-full max-w-md rounded-2xl bg-surface p-8 text-center shadow-lg">
          <div className="mb-3 text-5xl"><AlertTriangle size={48} className="text-amber-500 mx-auto" /></div>
          <h2 className="mb-2 text-lg font-bold text-text-primary">Bovino no encontrado</h2>
          <p className="mb-6 text-sm text-text-secondary">{error}</p>
          <Link
            to={`/farms/${farmId}`}
            className="inline-block rounded-lg bg-primary px-6 py-2.5 text-sm font-bold text-white no-underline hover:bg-primary-light"
          >
            Volver a la finca
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Cabecera */}
      <div className="rounded-2xl bg-surface p-6 shadow-sm">
        <div className="mb-4 flex items-center gap-3">
          <div className="flex items-center gap-2 text-4xl text-primary">
            {bovine.sex === "macho" ? (
              <svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="5" r="3"/><path d="M12 8v8"/><path d="M7 16a5 5 0 1 0 10 0"/></svg>
            ) : (
              <svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="5" r="3"/><path d="M12 8v8"/><circle cx="12" cy="17" r="4"/></svg>
            )}
          </div> {/* <- Corrección: Aquí faltaba cerrar este contenedor */}
          <div>
            <h1 className="text-2xl font-bold text-text-primary">
              {bovine.name ?? bovine.identification_number}
            </h1>
            <p className="text-sm text-text-muted">ID: {bovine.identification_number}</p>
          </div>
          <div className="ml-auto">
            <span
              className={`rounded-full px-3 py-1 text-sm font-medium ${
                bovine.status === "activo"
                  ? "bg-green-50 text-green-700"
                  : "bg-surface-alt text-text-secondary"
              }`}
            >
              {bovine.status}
            </span>
          </div>
        </div>
      </div>

      {/* Pestañas */}
      <div className="flex gap-1 rounded-xl bg-surface-alt p-1">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex flex-1 items-center justify-center gap-2 rounded-lg py-2 text-sm font-medium transition-colors ${
              activeTab === tab.id
                ? "bg-surface text-text-primary shadow-sm"
                : "text-text-secondary hover:text-text-secondary"
            }`}
          >
            <span>{tab.icon}</span>
            <span>{tab.label}</span>
          </button>
        ))}
      </div>

      {/* Pestaña General */}
      {activeTab === "general" && (
        <>
          <div className="rounded-2xl bg-surface p-6 shadow-sm">
            <h2 className="mb-4 text-lg font-bold text-text-primary">Datos generales</h2>
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
              <InfoCard label="Sexo" value={bovine.sex} />
              <InfoCard label="Raza" value={bovine.breed ?? "No registrada"} />
              <InfoCard label="Color" value={bovine.color ?? "No registrado"} />
              <InfoCard label="Propósito" value={bovine.purpose ?? "No especificado"} />
              <InfoCard label="Fecha nacimiento" value={bovine.birth_date ?? "—"} />
              <InfoCard
                label="Peso nacimiento"
                value={bovine.birth_weight ? `${bovine.birth_weight} kg` : "No registrado"}
              />
              <InfoCard
                label="Peso actual"
                value={bovine.current_weight ? `${bovine.current_weight} kg` : "No registrado"}
              />
              <InfoCard label="Fecha ingreso" value={bovine.entry_date ?? "—"} />
            </div>
          </div>

          <div className="rounded-2xl bg-surface p-6 shadow-sm">
            <h2 className="mb-4 text-lg font-bold text-text-primary">Trazabilidad</h2>
            <div className="space-y-3">
              <TraceItem
                icon={<ArrowDownToLine size={20} />}
                title={`Ingreso: ${bovine.entry_type}`}
                date={bovine.entry_date ?? ""}
                description={bovine.observations ?? undefined}
              />
              {bovine.exit_date && (
                <TraceItem
                  icon={<ArrowUpFromLine size={20} />}
                  title={`Salida: ${bovine.exit_reason ?? "sin motivo registrado"}`}
                  date={bovine.exit_date}
                />
              )}
              {bovine.father_id && (
                <TraceItem
                  icon={<Mars size={20} className="text-primary" />}
                  title="Padre registrado"
                  date=""
                  description={`ID padre: ${bovine.father_id}`}
                />
              )}
              {bovine.mother_id && (
                <TraceItem
                  icon={<Venus size={20} className="text-primary" />}
                  title="Madre registrada"
                  date=""
                  description={`ID madre: ${bovine.mother_id}`}
                />
              )}
              {bovine.markings && (
                <TraceItem icon={<Tag size={20} />} title="Marcas" date="" description={bovine.markings} />
              )}
            </div>
          </div>
        </>
      )}

      {/* Pestaña Productivo */}
      {activeTab === "productivo" && farmId && bovineId && (
        <>
          <WeightChart farmId={farmId} bovineId={bovineId} />
          <WeightHistory farmId={farmId} bovineId={bovineId} />
          <MilkProductionList farmId={farmId} bovineId={bovineId} />
          <FoodList farmId={farmId} bovineId={bovineId} />
        </>
      )}

      {/* Pestaña Reproductivo */}
      {activeTab === "reproductivo" && farmId && bovineId && (
        <ReproductiveTimeline farmId={farmId} bovineId={bovineId} />
      )}

      {/* Pestaña Sanitario */}
      {activeTab === "sanitario" && farmId && bovineId && (
        <TreatmentList farmId={farmId} bovineId={bovineId} />
      )}
    </div>
  );
}

{/* Componentes Auxiliares Locales */}
function InfoCard({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-xl bg-surface-alt p-4">
      <p className="text-xs font-medium text-text-muted uppercase tracking-wider">{label}</p>
      <p className="mt-1 text-sm font-semibold text-text-primary capitalize">{value}</p>
    </div>
  );
}

function TraceItem({ icon, title, date, description }: { icon: React.ReactNode; title: string; date: string; description?: string }) {
  return (
    <div className="flex gap-4 items-start rounded-xl p-3 hover:bg-surface-alt transition-colors">
      <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-primary-light/10 text-primary">
        {icon}
      </div>
      <div className="space-y-0.5">
        <h4 className="text-sm font-semibold text-text-primary">{title}</h4>
        {date && <p className="text-xs text-text-muted">{date}</p>}
        {description && <p className="text-sm text-text-secondary mt-1">{description}</p>}
      </div>
    </div>
  );
}
