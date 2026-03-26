import { Link, Outlet, useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";
import Breadcrumbs from "./Breadcrumbs";

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
    <div className="flex min-h-screen flex-col bg-cream">
      {/* Navbar */}
      <header className="sticky top-0 z-50 border-b-2 border-primary-light bg-white px-8">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between">
          <Link to="/dashboard" className="flex items-center gap-2 no-underline hover:opacity-85">
            <img src="/Logo_BoviTrack.png" alt="BoviTrack" className="h-[52px] w-auto object-contain" />
          </Link>

          <nav className="flex items-center gap-4">
            <Link
              to="/dashboard"
              className={`text-sm font-medium no-underline transition-colors hover:text-primary ${
                isActive("/dashboard") || isActive("/farms")
                  ? "border-b-2 border-primary pb-0.5 text-primary"
                  : "text-gray-700"
              }`}
            >
              Mis Fincas
            </Link>
            <div className="text-right leading-tight">
              <p className="text-sm text-gray-700">
                {user?.first_name} {user?.last_name}
              </p>
              {user?.role_name && (
                <p className="text-xs uppercase tracking-wide text-gray-500">
                  Rol: {user.role_name}
                </p>
              )}
            </div>
            <button
              onClick={handleLogout}
              className="rounded-lg border border-gray-300 bg-white px-3 py-1.5 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-50"
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
      <footer className="border-t border-gray-200 bg-white py-3 text-center text-xs text-gray-400">
        © {new Date().getFullYear()} BoviTrack — Gestión Ganadera Inteligente
      </footer>
    </div>
  );
}
