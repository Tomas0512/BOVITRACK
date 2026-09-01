import { useState } from "react";
import { Link, Outlet, useNavigate } from "react-router-dom";
import { Menu } from "lucide-react";
import { useAuth } from "../../hooks/useAuth";
import { deleteAccount } from "../../api/auth";
import Breadcrumbs from "./Breadcrumbs";
import Sidebar from "./Sidebar";
import ThemeToggle from "./ThemeToggle";

export default function AppLayout() {
  const { logout } = useAuth();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [showDelete, setShowDelete] = useState(false);
  const [deleteStep, setDeleteStep] = useState<1 | 2>(1);
  const [confirmText, setConfirmText] = useState("");
  const [delLoading, setDelLoading] = useState(false);
  const [delError, setDelError] = useState("");

  const resetDelete = () => {
    setShowDelete(false);
    setDeleteStep(1);
    setConfirmText("");
    setDelError("");
  };

  const handleDeleteAccount = async () => {
    setDelLoading(true);
    setDelError("");
    try {
      await deleteAccount();
      resetDelete();
      logout();
      navigate("/login");
    } catch (err: unknown) {
      setDelError(
        err instanceof Error && err.message
          ? err.message
          : "No se pudo eliminar la cuenta."
      );
    } finally {
      setDelLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar
        open={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        onRequestDelete={() => setShowDelete(true)}
      />

      <div className="flex min-w-0 flex-1 flex-col">
        {/* Navbar */}
        <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b-2 border-primary-light bg-surface px-4">
          <div className="flex items-center gap-2">
            <button
              onClick={() => setSidebarOpen((v) => !v)}
              className="rounded-lg p-2 text-text-secondary transition-colors hover:bg-surface-alt lg:hidden"
              aria-label="Abrir menú"
            >
              <Menu size={22} />
            </button>
            <ThemeToggle />
          </div>

          <Link to="/dashboard" className="flex items-center gap-2 no-underline hover:opacity-85">
            <img src="/Logo_BoviTrack.png" alt="BoviTrack" className="h-[52px] w-auto object-contain" />
          </Link>
        </header>

        {/* Modal de eliminación de cuenta (doble confirmación) */}
        {showDelete && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
            <div className="w-full max-w-md rounded-2xl bg-surface p-6 shadow-xl">
              {deleteStep === 1 ? (
                <>
                  <h2 className="mb-2 text-lg font-bold text-primary">¿Eliminar tu cuenta?</h2>
                  <p className="mb-4 text-sm text-text-secondary">
                    Perderás el acceso a BoviTrack y se cerrarán todas tus sesiones. Tus
                    registros se conservan. Esta acción no se puede deshacer.
                  </p>
                  <div className="flex gap-2">
                    <button
                      onClick={resetDelete}
                      className="flex-1 rounded-lg border border-border px-4 py-2 text-sm font-medium text-text-secondary hover:bg-surface-alt"
                    >
                      Cancelar
                    </button>
                    <button
                      onClick={() => setDeleteStep(2)}
                      className="flex-1 rounded-lg bg-red-600 px-4 py-2 text-sm font-bold text-white hover:bg-red-700"
                    >
                      Continuar
                    </button>
                  </div>
                </>
              ) : (
                <>
                  <h2 className="mb-2 text-lg font-bold text-primary">Confirmación final</h2>
                  <p className="mb-3 text-sm text-text-secondary">
                    Escribe <strong>ELIMINAR</strong> para confirmar de forma definitiva.
                  </p>
                  {delError && (
                    <div className="mb-3 rounded-lg bg-red-50 px-4 py-2 text-sm text-red-700">
                      {delError}
                    </div>
                  )}
                  <input
                    type="text"
                    value={confirmText}
                    onChange={(e) => {
                      setConfirmText(e.target.value);
                      if (delError) setDelError("");
                    }}
                    placeholder="ELIMINAR"
                    className="mb-4 w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none"
                  />
                  <div className="flex gap-2">
                    <button
                      onClick={resetDelete}
                      className="flex-1 rounded-lg border border-border px-4 py-2 text-sm font-medium text-text-secondary hover:bg-surface-alt"
                    >
                      Cancelar
                    </button>
                    <button
                      onClick={handleDeleteAccount}
                      disabled={confirmText.trim().toUpperCase() !== "ELIMINAR" || delLoading}
                      className="flex-1 rounded-lg bg-red-600 px-4 py-2 text-sm font-bold text-white hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {delLoading ? "Eliminando…" : "Eliminar cuenta"}
                    </button>
                  </div>
                </>
              )}
            </div>
          </div>
        )}

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
    </div>
  );
}
