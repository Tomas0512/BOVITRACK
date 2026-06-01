import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { getBovine, type BovineResponse } from "../api/bovines";
import WeightChart from "../components/bovines/WeightChart";
import WeightHistory from "../components/bovines/WeightHistory";
import MilkProductionList from "../components/bovines/MilkProductionList";
import FoodList from "../components/bovines/FoodList";
import TreatmentList from "../components/bovines/TreatmentList";

type Tab = "general" | "productivo" | "sanitario";

const TABS: { id: Tab; label: string; icon: string }[] = [
  { id: "general", label: "General", icon: "📋" },
  { id: "productivo", label: "Productivo", icon: "📊" },
  { id: "sanitario", label: "Sanitario", icon: "💉" },
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
        <div className="w-full max-w-md rounded-2xl bg-white p-8 text-center shadow-lg">
          <div className="mb-3 text-5xl">⚠️</div>
          <h2 className="mb-2 text-lg font-bold text-gray-800">Bovino no encontrado</h2>
          <p className="mb-6 text-sm text-gray-500">{error}</p>
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
      <div className="rounded-2xl bg-white p-6 shadow-sm">
        <div className="mb-4 flex items-center gap-3">
          <span className="text-4xl">{bovine.sex === "macho" ? "🐂" : "🐄"}</span>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              {bovine.name ?? bovine.identification_number}
            </h1>
            <p className="text-sm text-gray-400">ID: {bovine.identification_number}</p>
          </div>
          <div className="ml-auto">
            <span
              className={`rounded-full px-3 py-1 text-sm font-medium ${
                bovine.status === "activo"
                  ? "bg-green-50 text-green-700"
                  : "bg-gray-100 text-gray-600"
              }`}
            >
              {bovine.status}
            </span>
          </div>
        </div>
      </div>

      {/* Pestañas */}
      <div className="flex gap-1 rounded-xl bg-gray-100 p-1">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex flex-1 items-center justify-center gap-2 rounded-lg py-2 text-sm font-medium transition-colors ${
              activeTab === tab.id
                ? "bg-white text-gray-900 shadow-sm"
                : "text-gray-500 hover:text-gray-700"
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
          <div className="rounded-2xl bg-white p-6 shadow-sm">
            <h2 className="mb-4 text-lg font-bold text-gray-900">Datos generales</h2>
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

          <div className="rounded-2xl bg-white p-6 shadow-sm">
            <h2 className="mb-4 text-lg font-bold text-gray-900">Trazabilidad</h2>
            <div className="space-y-3">
              <TraceItem
                icon="📥"
                title={`Ingreso: ${bovine.entry_type}`}
                date={bovine.entry_date ?? ""}
                description={bovine.observations ?? undefined}
              />
              {bovine.exit_date && (
                <TraceItem
                  icon="📤"
                  title={`Salida: ${bovine.exit_reason ?? "sin motivo registrado"}`}
                  date={bovine.exit_date}
                />
              )}
              {bovine.father_id && (
                <TraceItem
                  icon="🐂"
                  title="Padre registrado"
                  date=""
                  description={`ID padre: ${bovine.father_id}`}
                />
              )}
              {bovine.mother_id && (
                <TraceItem
                  icon="🐄"
                  title="Madre registrada"
                  date=""
                  description={`ID madre: ${bovine.mother_id}`}
                />
              )}
              {bovine.markings && (
                <TraceItem icon="🏷️" title="Marcas" date="" description={bovine.markings} />
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

      {/* Pestaña Sanitario */}
      {activeTab === "sanitario" && farmId && bovineId && (
        <TreatmentList farmId={farmId} bovineId={bovineId} />
      )}

      {/* Botón volver */}
      <div>
        <Link
          to={`/farms/${farmId}`}
          className="inline-block rounded-lg border border-gray-200 px-4 py-2 text-sm font-medium text-gray-600 no-underline hover:bg-gray-50"
        >
          ← Volver a la finca
        </Link>
      </div>
    </div>
  );
}

function InfoCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-gray-100 bg-surface p-3">
      <p className="mb-0.5 text-xs font-semibold uppercase tracking-wide text-gray-400">{label}</p>
      <p className="text-sm font-medium text-gray-800">{value}</p>
    </div>
  );
}

function TraceItem({ icon, title, date, description }: { icon: string; title: string; date: string; description?: string }) {
  return (
    <div className="flex items-start gap-3 rounded-lg border border-gray-100 p-3">
      <span className="text-xl">{icon}</span>
      <div>
        <p className="font-medium text-gray-800">{title}</p>
        {date && <p className="text-xs text-gray-400">{date}</p>}
        {description && <p className="mt-1 text-sm text-gray-500">{description}</p>}
      </div>
    </div>
  );
}
