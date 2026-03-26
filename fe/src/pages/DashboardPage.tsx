import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { listFarms, type FarmResponse } from "../api/farms";
import { useAuth } from "../hooks/useAuth";

export default function DashboardPage() {
  const { user } = useAuth();
  const [farms, setFarms] = useState<FarmResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const load = async () => {
      try {
        const data = await listFarms();
        setFarms(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Error al cargar fincas");
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  return (
    <div>
      {/* Header */}
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            ¡Hola, {user?.first_name}! 👋
          </h1>
          <p className="mt-1 text-sm text-gray-500">Gestiona tus fincas ganaderas</p>
          {user?.role_name && (
            <p className="mt-1 text-xs uppercase tracking-wide text-gray-500">
              Rol en sesión: {user.role_name}
            </p>
          )}
        </div>
        <Link
          to="/farms/new"
          className="rounded-lg bg-primary px-4 py-2.5 text-sm font-bold text-white no-underline transition-colors hover:bg-primary-light"
        >
          + Crear finca
        </Link>
      </div>

      {/* Estado de carga */}
      {loading && (
        <div className="flex justify-center py-12">
          <div className="h-10 w-10 animate-spin rounded-full border-4 border-primary border-t-transparent" />
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-center text-sm text-red-600">
          {error}
        </div>
      )}

      {/* Sin fincas */}
      {!loading && !error && farms.length === 0 && (
        <div className="rounded-2xl bg-white p-12 text-center shadow-sm">
          <div className="mb-3 text-5xl">🏡</div>
          <h2 className="mb-2 text-lg font-bold text-gray-800">Aún no tienes fincas</h2>
          <p className="mb-6 text-sm text-gray-500">
            Crea tu primera finca para empezar a gestionar tu ganado.
          </p>
          <Link
            to="/farms/new"
            className="inline-block rounded-lg bg-primary px-6 py-2.5 text-sm font-bold text-white no-underline transition-colors hover:bg-primary-light"
          >
            Crear mi primera finca
          </Link>
        </div>
      )}

      {/* Lista de fincas */}
      {!loading && farms.length > 0 && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {farms.map((farm) => (
            <Link
              key={farm.id}
              to={`/farms/${farm.id}`}
              className="group rounded-xl bg-white p-5 shadow-sm transition-shadow no-underline hover:shadow-md"
            >
              <div className="mb-2 flex items-center gap-2">
                <span className="text-2xl">🐄</span>
                <h3 className="text-base font-bold text-gray-900 group-hover:text-primary">
                  {farm.name}
                </h3>
              </div>
              <p className="mb-1 text-sm text-gray-500">{farm.address}</p>
              <div className="flex items-center gap-3 text-xs text-gray-400">
                <span>{farm.total_area} {farm.area_unit}</span>
                <span>ID: {farm.farm_identifier}</span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
