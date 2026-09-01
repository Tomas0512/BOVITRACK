import { useEffect, useState, type ReactNode } from "react";
import { Link } from "react-router-dom";
import {
  Beef,
  Building2,
  Droplets,
  Plus,
  LayoutDashboard,
  Sprout,
  Pill,
  Wheat,
  ArrowLeftRight,
  Map,
  FileText,
  Users,
  BarChart3,
  Wallet,
  Bell,
} from "lucide-react";
import { useFarm } from "../context/FarmContext";
import { listBovines } from "../api/bovines";
import { listLandPlots } from "../api/land_plots";
import { listMilkProduction } from "../api/milk_production";
import { useAuth } from "../hooks/useAuth";

// Fotografía de ganado (si falla, el banner muestra el degradado).
const BANNER_IMG =
  "https://images.unsplash.com/photo-1560493676-04071c5f467b?auto=format&fit=crop&w=1200&q=60";

const kpi = (value: string | number, label: string, icon: ReactNode, tint: string) => ({
  value,
  label,
  icon,
  tint,
});

interface ModuleCard {
  id: string;
  label: string;
  icon: ReactNode;
  tab?: string;
  route?: string;
}

const MODULES: ModuleCard[] = [
  { id: "bovinos", label: "Ganado", icon: <Beef size={22} />, tab: "bovinos" },
  { id: "terneros", label: "Terneros", icon: <Sprout size={22} />, tab: "terneros" },
  { id: "sanidad", label: "Sanidad", icon: <Pill size={22} />, tab: "sanidad" },
  { id: "alimentacion", label: "Alimentación", icon: <Wheat size={22} />, tab: "alimentacion" },
  { id: "movimientos", label: "Movimientos", icon: <ArrowLeftRight size={22} />, tab: "movimientos" },
  { id: "lotes", label: "Lotes y Potreros", icon: <Map size={22} />, tab: "lotes" },
  { id: "documentos", label: "Documentos", icon: <FileText size={22} />, tab: "documentos" },
  { id: "empleados", label: "Empleados", icon: <Users size={22} />, tab: "empleados" },
  { id: "auditoria", label: "Auditoría", icon: <FileText size={22} />, tab: "auditoria" },
  { id: "reports", label: "Reportes", icon: <BarChart3 size={22} />, route: "/reports" },
  { id: "economics", label: "Economía", icon: <Wallet size={22} />, route: "/economics" },
  { id: "alerts", label: "Alertas", icon: <Bell size={22} />, route: "/alerts" },
];

export default function DashboardPage() {
  const { user } = useAuth();
  const { farms, activeFarm, activeFarmId, loading } = useFarm();
  const [animals, setAnimals] = useState(0);
  const [lots, setLots] = useState(0);
  const [milk, setMilk] = useState(0);
  const [bannerOk, setBannerOk] = useState(true);

  useEffect(() => {
    if (!activeFarmId) return;
    let cancelled = false;
    Promise.all([
      listBovines(activeFarmId),
      listLandPlots(activeFarmId, true),
      listMilkProduction(activeFarmId),
    ])
      .then(([bov, lands, milks]) => {
        if (cancelled) return;
        setAnimals(bov.length);
        setLots(lands.length);
        setMilk(milks.reduce((sum, m) => sum + Number(m.quantity_liters || 0), 0));
      })
      .catch(() => {});
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

  const moduleTo = (m: ModuleCard) => {
    const suffix = m.tab ? `?tab=${m.tab}` : m.route ?? "";
    return `/farms/${activeFarmId}${suffix}`;
  };

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

      {/* Módulos */}
      <div className="rounded-2xl bg-surface p-5 shadow-sm">
        <div className="mb-4 flex items-center gap-2">
          <LayoutDashboard size={18} className="text-primary" />
          <h2 className="text-base font-bold text-text-primary">Módulos</h2>
        </div>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {MODULES.map((m) => (
            <Link
              key={m.id}
              to={moduleTo(m)}
              className="flex items-center gap-3 rounded-xl border border-border bg-surface p-4 no-underline transition-colors hover:border-primary/40 hover:bg-surface-alt"
            >
              <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-primary/10 text-primary">
                {m.icon}
              </span>
              <span className="text-sm font-medium text-text-primary">{m.label}</span>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
