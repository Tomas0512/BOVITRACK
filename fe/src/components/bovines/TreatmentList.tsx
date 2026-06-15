import { useEffect, useState } from "react";
import { Syringe } from "lucide-react";
import { listTreatments, type TreatmentResponse } from "../../api/treatments";

interface Props {
  farmId: string;
  bovineId: string;
}

const TREATMENT_TYPE_LABELS: Record<string, string> = {
  vacunacion: "Vacunación",
  desparasitacion: "Desparasitación",
  antibiotico: "Antibiótico",
  antiparasitario: "Antiparasitario",
  vitamina: "Vitamina",
  cirugia: "Cirugía",
  otro: "Otro",
};

const ROUTE_LABELS: Record<string, string> = {
  oral: "Oral",
  intramuscular: "Intramuscular",
  subcutanea: "Subcutánea",
  intravenosa: "Intravenosa",
  topica: "Tópica",
};

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString("es-CO", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  });
}

function daysUntil(isoDate: string): number {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const target = new Date(isoDate);
  target.setHours(0, 0, 0, 0);
  return Math.round((target.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));
}

export default function TreatmentList({ farmId, bovineId }: Props) {
  const [treatments, setTreatments] = useState<TreatmentResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    setLoading(true);
    listTreatments(farmId, bovineId)
      .then(setTreatments)
      .catch(() => setError("No se pudo cargar los tratamientos sanitarios."))
      .finally(() => setLoading(false));
  }, [farmId, bovineId]);

  return (
    <div className="rounded-2xl bg-white p-6 shadow-sm">
      <h3 className="mb-4 font-bold text-gray-900"><Syringe size={18} className="inline-block mr-1.5 -mt-0.5" /> Tratamientos sanitarios</h3>

      {loading && (
        <div className="flex justify-center py-8">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
        </div>
      )}
      {error && (
        <p className="py-4 text-center text-sm text-red-500">{error}</p>
      )}
      {!loading && !error && treatments.length === 0 && (
        <p className="py-6 text-center text-sm text-gray-400">
          Sin tratamientos registrados para este animal.
        </p>
      )}
      {!loading && !error && treatments.length > 0 && (
        <div className="space-y-3">
          {treatments.map((t) => {
            const days = t.next_application_date ? daysUntil(t.next_application_date) : null;
            const isUpcoming = days !== null && days >= 0 && days <= 7;
            const isOverdue = days !== null && days < 0;

            return (
              <div
                key={t.id}
                className={`rounded-xl border p-4 ${
                  isOverdue
                    ? "border-red-200 bg-red-50"
                    : isUpcoming
                    ? "border-amber-200 bg-amber-50"
                    : "border-gray-100 bg-gray-50"
                }`}
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-start gap-3">
                    <Syringe size={20} className="mt-0.5 shrink-0 text-red-500" />
                    <div>
                      <p className="font-semibold text-gray-800">
                        {TREATMENT_TYPE_LABELS[t.treatment_type] ?? t.treatment_type}:{" "}
                        {t.product_name}
                      </p>
                      <p className="text-xs text-gray-400">
                        {formatDate(t.application_date)}
                      </p>
                      <p className="mt-1 text-sm text-gray-600">
                        Dosis: <span className="font-medium">{t.dose}</span> · Vía:{" "}
                        <span className="font-medium">
                          {ROUTE_LABELS[t.administration_route] ?? t.administration_route}
                        </span>
                      </p>
                      {t.diagnosis && (
                        <p className="mt-1 text-sm text-gray-500">
                          Diagnóstico: {t.diagnosis}
                        </p>
                      )}
                      {t.symptoms && (
                        <p className="text-sm text-gray-500">Síntomas: {t.symptoms}</p>
                      )}
                      {t.observations && (
                        <p className="mt-1 text-xs text-gray-400">{t.observations}</p>
                      )}
                    </div>
                  </div>

                  {/* Badge próxima aplicación */}
                  {t.next_application_date && (
                    <div className="shrink-0 text-right">
                      <p className="text-xs text-gray-400">Próx. aplicación</p>
                      <p
                        className={`text-sm font-semibold ${
                          isOverdue
                            ? "text-red-600"
                            : isUpcoming
                            ? "text-amber-600"
                            : "text-gray-700"
                        }`}
                      >
                        {formatDate(t.next_application_date)}
                      </p>
                      {days !== null && (
                        <p
                          className={`text-xs ${
                            isOverdue
                              ? "text-red-500"
                              : isUpcoming
                              ? "text-amber-500"
                              : "text-gray-400"
                          }`}
                        >
                          {isOverdue
                            ? `Vencido hace ${Math.abs(days)} días`
                            : days === 0
                            ? "Hoy"
                            : `En ${days} días`}
                        </p>
                      )}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
