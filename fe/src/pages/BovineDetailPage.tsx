import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { getBovine, type BovineResponse } from "../api/bovines";
import { listTreatments, type TreatmentResponse } from "../api/treatments";
import { listMilkProduction, type MilkProductionResponse } from "../api/milk_production";

export default function BovineDetailPage() {
  const { farmId, bovineId } = useParams<{ farmId: string; bovineId: string }>();
  const [bovine, setBovine] = useState<BovineResponse | null>(null);
  const [treatments, setTreatments] = useState<TreatmentResponse[]>([]);
  const [milkRecords, setMilkRecords] = useState<MilkProductionResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!farmId || !bovineId) return;
    Promise.all([
      getBovine(farmId, bovineId),
      listTreatments(farmId, bovineId).catch(() => [] as TreatmentResponse[]),
      listMilkProduction(farmId, bovineId).catch(() => [] as MilkProductionResponse[]),
    ])
      .then(([b, t, m]) => { setBovine(b); setTreatments(t); setMilkRecords(m); })
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
          <Link to={`/farms/${farmId}`}
            className="inline-block rounded-lg bg-primary px-6 py-2.5 text-sm font-bold text-white no-underline hover:bg-primary-light">
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
            <span className={`rounded-full px-3 py-1 text-sm font-medium ${bovine.status === "activo" ? "bg-green-50 text-green-700" : "bg-gray-100 text-gray-600"}`}>
              {bovine.status}
            </span>
          </div>
        </div>

        {/* Datos generales */}
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <InfoCard label="Sexo" value={bovine.sex} />
          <InfoCard label="Raza" value={bovine.breed ?? "No registrada"} />
          <InfoCard label="Color" value={bovine.color ?? "No registrado"} />
          <InfoCard label="Propósito" value={bovine.purpose ?? "No especificado"} />
          <InfoCard label="Fecha nacimiento" value={bovine.birth_date} />
          <InfoCard label="Peso nacimiento" value={bovine.birth_weight ? `${bovine.birth_weight} kg` : "No registrado"} />
          <InfoCard label="Peso actual" value={bovine.current_weight ? `${bovine.current_weight} kg` : "No registrado"} />
          <InfoCard label="Fecha ingreso" value={bovine.entry_date} />
        </div>
      </div>

      {/* Trazabilidad */}
      <div className="rounded-2xl bg-white p-6 shadow-sm">
        <h2 className="mb-4 text-lg font-bold text-gray-900">Trazabilidad</h2>
        <div className="space-y-3">
          <TraceItem
            icon="📥"
            title={`Ingreso: ${bovine.entry_type}`}
            date={bovine.entry_date}
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
            <TraceItem icon="🐂" title="Padre registrado" date="" description={`ID padre: ${bovine.father_id}`} />
          )}
          {bovine.mother_id && (
            <TraceItem icon="🐄" title="Madre registrada" date="" description={`ID madre: ${bovine.mother_id}`} />
          )}
          {bovine.markings && (
            <TraceItem icon="🏷️" title="Marcas" date="" description={bovine.markings} />
          )}
        </div>
      </div>

      {/* Tratamientos sanitarios */}
      <div className="rounded-2xl bg-white p-6 shadow-sm">
        <h2 className="mb-4 text-lg font-bold text-gray-900">Tratamientos sanitarios</h2>
        {treatments.length === 0 ? (
          <p className="text-sm text-gray-400">No hay tratamientos registrados para este bovino</p>
        ) : (
          <div className="space-y-3">
            {treatments.map((t) => (
              <div key={t.id} className="flex items-start gap-3 rounded-lg border border-gray-100 p-3">
                <span className="text-xl">💉</span>
                <div className="flex-1">
                  <p className="font-medium text-gray-800">{t.treatment_type}: {t.product_name}</p>
                  <p className="text-xs text-gray-400">{new Date(t.application_date).toLocaleDateString("es-CO")}</p>
                  <p className="text-sm text-gray-500">Dosis: {t.dose} · Vía: {t.administration_route}</p>
                  {t.diagnosis && <p className="text-sm text-gray-500">Diagnóstico: {t.diagnosis}</p>}
                  {t.observations && <p className="text-sm text-gray-400">{t.observations}</p>}
                  {t.next_application_date && (
                    <p className="text-xs text-blue-600">Próx. aplicación: {t.next_application_date}</p>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Producción lechera */}
      <div className="rounded-2xl bg-white p-6 shadow-sm">
        <h2 className="mb-4 text-lg font-bold text-gray-900">Producción lechera</h2>
        {milkRecords.length === 0 ? (
          <p className="text-sm text-gray-400">No hay registros de ordeño para este bovino</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-100 text-left text-xs font-semibold uppercase tracking-wide text-gray-400">
                  <th className="pb-2 pr-4">Fecha</th>
                  <th className="pb-2 pr-4">Litros</th>
                  <th className="pb-2 pr-4">Tipo</th>
                  <th className="pb-2 pr-4">Sesión</th>
                  <th className="pb-2">Observaciones</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {milkRecords.map((m) => (
                  <tr key={m.id} className="hover:bg-gray-50">
                    <td className="py-2 pr-4 text-gray-600">{new Date(m.milking_date).toLocaleDateString("es-CO")}</td>
                    <td className="py-2 pr-4 font-medium text-gray-800">{m.quantity_liters} L</td>
                    <td className="py-2 pr-4 text-gray-600">{m.milking_type}</td>
                    <td className="py-2 pr-4 text-gray-500">{m.milking_session ?? "-"}</td>
                    <td className="py-2 text-gray-400">{m.observations ?? "-"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Botón volver */}
      <div>
        <Link to={`/farms/${farmId}`}
          className="inline-block rounded-lg border border-gray-200 px-4 py-2 text-sm font-medium text-gray-600 no-underline hover:bg-gray-50">
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
