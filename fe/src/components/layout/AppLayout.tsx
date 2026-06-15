import { Link, Outlet, useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";
import Breadcrumbs from "./Breadcrumbs";
import ThemeToggle from "./ThemeToggle";

export default function AppLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const { pathname } = useLocation();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const isActive = (path: string) =>
    pathname === path || pathname.startsWith(path + "/");

  return (
    <div className="flex min-h-screen flex-col bg-background">
      {/* Navbar */}
      <header className="sticky top-0 z-50 border-b-2 border-primary-light bg-surface px-8">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between">
          <Link to="/dashboard" className="flex items-center gap-2 no-underline hover:opacity-85">
            <img src="/Logo_BoviTrack.png" alt="BoviTrack" className="h-[52px] w-auto object-contain" />
          </Link>

          <nav className="flex items-center gap-4">
            <ThemeToggle />
            <Link
              to="/dashboard"
              className={`text-sm font-medium no-underline transition-colors hover:text-primary ${
                isActive("/dashboard") || isActive("/farms")
                  ? "border-b-2 border-primary pb-0.5 text-primary"
                  : "text-text-secondary"
              }`}
            >
              Mis Fincas
            </Link>
            <div className="text-right leading-tight">
              <p className="text-sm text-text-primary">
                {user?.first_name} {user?.last_name}
              </p>
              {user?.role_name && (
                <p className="text-xs uppercase tracking-wide text-text-muted">
                  Rol: {user.role_name}
                </p>
              )}
            </div>
            <button
              onClick={handleLogout}
              className="rounded-lg border border-border bg-surface px-3 py-1.5 text-sm font-medium text-text-secondary transition-colors hover:bg-surface-alt"
            >
              Cerrar sesión
            </button>
          </nav>
        </div>
      </header>

      {/* Contenido */}
      <main className="mx-auto w-full max-w-6xl flex-1 px-4 py-6">
        <Breadcrumbs />
        <Outlet />
      </main>

      {/* Footer */}
      <footer className="border-t border-border bg-surface py-3 text-center text-xs text-text-muted">
        © {new Date().getFullYear()} BoviTrack — Gestión Ganadera Inteligente
      </footer>
    </div>
  );
}
