import { useEffect, useState, type ReactNode } from "react";
import { Link } from "react-router-dom";
import { Beef, Building2, Droplets, Plus, Clock } from "lucide-react";
import { useFarm } from "../context/FarmContext";
import { listBovines } from "../api/bovines";
import { listLandPlots } from "../api/land_plots";
import { listMilkProduction } from "../api/milk_production";
import { listAuditLogs, type AuditLogEntry } from "../api/audit_logs";
import { useAuth } from "../hooks/useAuth";

const ACTIVITY_LABEL: Record<string, string> = {
  "create:bovine": "Bovino registrado",
  "update:bovine": "Bovino actualizado",
  "create:milk_production": "Ordeño registrado",
  "create:weight": "Pesaje registrado",
  "create:treatment": "Tratamiento aplicado",
  "create:sanitary_plan": "Plan sanitario creado",
  "create:reproductive_event": "Evento reproductivo registrado",
  "create:economic_record": "Movimiento económico registrado",
  "create:movement": "Movimiento de animal registrado",
  "create:food": "Insumo registrado",
  "create:consumption": "Consumo de insumo registrado",
  "create:farm_invitation": "Invitación enviada",
  "register": "Cuenta creada",
  "login": "Inicio de sesión",
  "logout": "Cierre de sesión",
};

// Fotografía de ganado (si falla, el banner muestra el degradado).
const BANNER_IMG =
  "https://images.unsplash.com/photo-1560493676-04071c5f467b?auto=format&fit=crop&w=1200&q=60";

const kpi = (value: string | number, label: string, icon: ReactNode, tint: string) => ({
  value,
  label,
  icon,
  tint,
});

export default function DashboardPage() {
  const { user } = useAuth();
  const { farms, activeFarm, activeFarmId, loading } = useFarm();
  const [animals, setAnimals] = useState(0);
  const [lots, setLots] = useState(0);
  const [milk, setMilk] = useState(0);
  const [activities, setActivities] = useState<AuditLogEntry[]>([]);
  const [dataLoading, setDataLoading] = useState(true);
  const [error, setError] = useState("");
  const [bannerOk, setBannerOk] = useState(true);

  useEffect(() => {
    if (!activeFarmId) return;
    let cancelled = false;
    Promise.all([
      listBovines(activeFarmId),
      listLandPlots(activeFarmId, true),
      listMilkProduction(activeFarmId),
      listAuditLogs(activeFarmId),
    ])
      .then(([bov, lands, milks, logs]) => {
        if (cancelled) return;
        setAnimals(bov.length);
        setLots(lands.length);
        setMilk(milks.reduce((sum, m) => sum + Number(m.quantity_liters || 0), 0));
        setActivities(logs.slice(0, 5));
        setError("");
      })
      .catch(() => {
        setError("No se pudo cargar el resumen de la finca");
      })
      .finally(() => {
        if (!cancelled) setDataLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [activeFarmId]);

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  // Sin fincas
  if (farms.length === 0) {
    const canCreate = !user?.role_name || user.role_name === "Administrador";
    return (
      <div className="rounded-2xl bg-surface p-12 text-center shadow-sm">
        <div className="mb-3 text-primary"><Building2 size={48} className="mx-auto" /></div>
        <h2 className="mb-2 text-lg font-bold text-text-primary">Aún no tienes fincas</h2>
        <p className="mb-6 text-sm text-text-secondary">
          {canCreate
            ? "Crea tu primera finca para empezar a gestionar tu ganado."
            : "Espera a que un administrador te asigne a una finca."}
        </p>
        {canCreate && (
          <Link
            to="/farms/new"
            className="inline-block rounded-lg bg-primary px-6 py-2.5 text-sm font-bold text-white no-underline transition-colors hover:bg-primary-light"
          >
            Crear mi primera finca
          </Link>
        )}
      </div>
    );
  }

  // Sin finca activa seleccionable (por seguridad)
  if (!activeFarm) {
    return (
      <div className="rounded-2xl bg-surface p-12 text-center shadow-sm">
        <p className="text-sm text-text-secondary">Selecciona una finca del menú lateral.</p>
      </div>
    );
  }

  const cards = [
    kpi(animals, "Animales", <Beef size={24} />, "from-primary/15 to-accent/30"),
    kpi(lots, "Lotes activos", <Building2 size={24} />, "from-accent/30 to-cream"),
    kpi(milk.toLocaleString("es-CO") + " L", "Producción de leche", <Droplets size={24} />, "from-cream to-accent/20"),
  ];

  return (
    <div className="space-y-6">
      {/* Bienvenida + banner */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-primary/20 via-cream to-accent/30 shadow-sm">
        {bannerOk && (
          <img
            src={BANNER_IMG}
            alt=""
            onError={() => setBannerOk(false)}
            className="absolute inset-0 h-full w-full object-cover opacity-25"
          />
        )}
        <div className="relative z-10 flex flex-col gap-2 p-6 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <h1 className="text-2xl font-bold text-text-primary">
              Bienvenido, {user?.first_name}
            </h1>
            <p className="text-sm text-text-secondary">
              {activeFarm.name} · {activeFarm.city_municipality} · {activeFarm.total_area}{" "}
              {activeFarm.area_unit}
            </p>
          </div>
          {(!user?.role_name || user.role_name === "Administrador") && (
            <Link
              to="/farms/new"
              className="inline-flex items-center gap-1.5 rounded-lg bg-primary px-4 py-2 text-sm font-bold text-white no-underline transition-colors hover:bg-primary-light"
            >
              <Plus size={16} /> Crear finca
            </Link>
          )}
        </div>
      </div>

      {/* KPIs */}
      <div className="grid gap-4 sm:grid-cols-3">
        {cards.map((c) => (
          <div
            key={c.label}
            className="flex items-center gap-3 rounded-2xl bg-surface p-4 shadow-sm"
          >
            <div
              className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br ${c.tint} text-text-primary`}
            >
              {c.icon}
            </div>
            <div className="leading-tight">
              <p className="text-xl font-bold text-text-primary">{c.value}</p>
              <p className="text-xs text-text-muted">{c.label}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Últimas actividades */}
      <div className="rounded-2xl bg-surface p-5 shadow-sm">
        <div className="mb-3 flex items-center gap-2">
          <Clock size={18} className="text-primary" />
          <h2 className="text-base font-bold text-text-primary">Últimas actividades</h2>
        </div>
        {dataLoading ? (
          <div className="flex justify-center py-6">
            <div className="h-6 w-6 animate-spin rounded-full border-2 border-primary border-t-transparent" />
          </div>
        ) : activities.length === 0 ? (
          <p className="py-6 text-center text-sm text-text-muted">Sin actividad reciente.</p>
        ) : (
          <ul className="divide-y divide-border">
            {activities.map((a) => {
              const label = ACTIVITY_LABEL[`${a.action}:${a.entity}`] ?? `${a.action} · ${a.entity}`;
              return (
                <li key={a.id} className="flex items-center justify-between gap-2 py-2.5">
                  <div className="min-w-0">
                    <p className="truncate text-sm text-text-primary">{label}</p>
                    <p className="truncate text-xs text-text-muted">
                      {a.user_full_name ?? a.user_email ?? "Sistema"}
                    </p>
                  </div>
                  <span className="shrink-0 text-xs text-text-muted">
                    {new Date(a.created_at).toLocaleDateString("es-CO")}
                  </span>
                </li>
              );
            })}
          </ul>
        )}
      </div>

      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-center text-sm text-red-600">
          {error}
        </div>
      )}
    </div>
  );
}
