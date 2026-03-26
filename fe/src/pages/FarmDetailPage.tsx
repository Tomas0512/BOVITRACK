import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { getFarm, type FarmResponse } from "../api/farms";

export default function FarmDetailPage() {
  const { farmId } = useParams<{ farmId: string }>();
  const [farm, setFarm] = useState<FarmResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!farmId) return;
    const load = async () => {
      try {
        const data = await getFarm(farmId);
        setFarm(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Error al cargar la finca");
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [farmId]);

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
        </div>

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
