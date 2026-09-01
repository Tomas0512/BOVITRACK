import { useLocation, useNavigate, useSearchParams } from "react-router-dom";
import {
  Home,
  Beef,
  BarChart3,
  Wallet,
  Bell,
  ShieldCheck,
  LogOut,
  UserRound,
  Sprout,
  Pill,
  Wheat,
  ArrowLeftRight,
  Map,
  FileText,
  Users,
} from "lucide-react";
import type { JSX } from "react";
import { useAuth } from "../../hooks/useAuth";
import { useFarm } from "../../context/FarmContext";

interface NavItem {
  to: string;
  label: string;
  icon: JSX.Element;
  adminOnly?: boolean;
  tab?: string;
}

interface Props {
  open: boolean;
  onClose: () => void;
  onRequestDelete: () => void;
}

export default function Sidebar({ open, onClose, onRequestDelete }: Props) {
  const { user, logout } = useAuth();
  const { farms, activeFarmId, activeFarm, setActiveFarmId } = useFarm();
  const { pathname } = useLocation();
  const [searchParams] = useSearchParams();
  const currentTab = searchParams.get("tab");
  const navigate = useNavigate();

  const isActive = (path: string) => pathname === path || pathname.startsWith(path + "/");

  const go = (to: string) => {
    if (to && to !== "#") navigate(to);
    onClose();
  };

  const farm = (path: string) => (activeFarmId ? `/farms/${activeFarmId}${path}` : "#");
  const onFarmDetail = activeFarmId !== null && pathname === `/farms/${activeFarmId}`;

  const items: NavItem[] = [
    { to: "/dashboard", label: "Inicio", icon: <Home size={20} /> },
    { to: farm("?tab=bovinos"), label: "Ganado", icon: <Beef size={20} />, tab: "bovinos" },
    { to: farm("?tab=terneros"), label: "Terneros", icon: <Sprout size={20} />, tab: "terneros" },
    { to: farm("?tab=sanidad"), label: "Sanidad", icon: <Pill size={20} />, tab: "sanidad" },
    { to: farm("?tab=alimentacion"), label: "Alimentación", icon: <Wheat size={20} />, tab: "alimentacion" },
    { to: farm("?tab=movimientos"), label: "Movimientos", icon: <ArrowLeftRight size={20} />, tab: "movimientos" },
    { to: farm("?tab=lotes"), label: "Lotes y Potreros", icon: <Map size={20} />, tab: "lotes" },
    { to: farm("?tab=documentos"), label: "Documentos", icon: <FileText size={20} />, tab: "documentos" },
    { to: farm("?tab=empleados"), label: "Empleados", icon: <Users size={20} />, tab: "empleados" },
    { to: farm("?tab=auditoria"), label: "Auditoría", icon: <ShieldCheck size={20} />, tab: "auditoria" },
    { to: farm("/reports"), label: "Reportes", icon: <BarChart3 size={20} /> },
    { to: farm("/economics"), label: "Economía", icon: <Wallet size={20} /> },
    { to: farm("/alerts"), label: "Alertas", icon: <Bell size={20} /> },
    { to: "/audit", label: "Auditoría Global", icon: <ShieldCheck size={20} />, adminOnly: true },
  ];

  const visible = user?.role_name === "Administrador";

  const isItemActive = (item: NavItem) => {
    if (item.tab) return onFarmDetail && currentTab === item.tab;
    if (item.to === "/dashboard") return pathname === "/dashboard";
    if (item.to === "/audit") return pathname === "/audit";
    return isActive(item.to);
  };

  const initials = (user?.first_name?.[0] ?? "") + (user?.last_name?.[0] ?? "");

  return (
    <>
      {/* Overlay para móvil */}
      {open && (
        <div
          className="fixed inset-0 z-40 bg-black/40 lg:hidden"
          onClick={onClose}
          aria-hidden="true"
        />
      )}

      <aside
        className={`fixed inset-y-0 left-0 z-50 flex w-64 flex-col border-r border-border bg-surface transition-transform duration-200 lg:static lg:translate-x-0 ${
          open ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        {/* Marca */}
        <div className="flex h-16 items-center gap-2 border-b border-border px-4">
          <img src="/Logo_BoviTrack.png" alt="BoviTrack" className="h-10 w-auto object-contain" />
        </div>

        {/* Selector de finca activa */}
        <div className="px-4 pt-4">
          <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-text-muted">
            Finca activa
          </p>
          <select
            value={activeFarmId ?? ""}
            onChange={(e) => {
              if (e.target.value) {
                setActiveFarmId(e.target.value);
                onClose();
              }
            }}
            className="w-full rounded-lg border border-border bg-surface px-2 py-1.5 text-sm text-text-primary focus:border-primary focus:outline-none"
          >
            {!activeFarmId && <option value="">Selecciona una finca…</option>}
            {farms.map((f) => (
              <option key={f.id} value={f.id}>
                {f.name}
              </option>
            ))}
          </select>
          {activeFarm && (
            <p className="mt-1 truncate text-xs text-text-muted">
              {activeFarm.total_area} {activeFarm.area_unit} · {activeFarm.farm_identifier}
            </p>
          )}
        </div>

        {/* Navegación */}
        <nav className="mt-4 flex-1 space-y-1 px-3">
          {items
            .filter((i) => !i.adminOnly || visible)
            .map((item) => {
              const active = item.to !== "#" && isItemActive(item);
              return (
                <button
                  key={item.label}
                  onClick={() => go(item.to)}
                  className={`flex w-full items-center gap-3 rounded-lg px-3 py-2 text-left text-sm font-medium transition-colors ${
                    active
                      ? "bg-primary text-white"
                      : "text-text-secondary hover:bg-surface-alt hover:text-text-primary"
                  }`}
                >
                  <span className={active ? "" : "text-primary"}>{item.icon}</span>
                  {item.label}
                </button>
              );
            })}
        </nav>

        {/* Usuario */}
        <div className="border-t border-border p-3">
          <div className="mb-2 flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-full bg-primary text-sm font-bold text-white">
              {initials || <UserRound size={18} />}
            </div>
            <div className="leading-tight">
              <p className="text-sm font-medium text-text-primary">
                {user?.first_name} {user?.last_name}
              </p>
              {user?.role_name && (
                <p className="text-xs uppercase tracking-wide text-text-muted">{user.role_name}</p>
              )}
            </div>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => {
                logout();
                navigate("/login");
              }}
              className="flex flex-1 items-center justify-center gap-1.5 rounded-lg border border-border px-2 py-1.5 text-xs font-medium text-text-secondary transition-colors hover:bg-surface-alt"
            >
              <LogOut size={14} /> Salir
            </button>
            <button
              onClick={onRequestDelete}
              className="flex-1 rounded-lg border border-red-200 bg-red-50 px-2 py-1.5 text-xs font-medium text-red-600 transition-colors hover:bg-red-100"
            >
              Eliminar cuenta
            </button>
          </div>
        </div>
      </aside>
    </>
  );
}
