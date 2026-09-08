import { useEffect, useRef, useState } from "react";
import { useNavigate, Outlet } from "react-router-dom";
import { LogOut, Menu, Pencil, Plus, Tractor, Trash2 } from "lucide-react";
import { useAuth } from "../../hooks/useAuth";
import { deleteAccount } from "../../api/auth";
import {
  updateFarm,
  deleteFarm,
  listDepartments,
  listPurposes,
  type FarmRequest,
  type DepartmentOption,
  type PurposeOption,
} from "../../api/farms";
import { useFarm } from "../../context/FarmContext";
import Sidebar from "./Sidebar";
import ThemeToggle from "./ThemeToggle";
import SessionGuard from "../SessionGuard";
import ConfirmDialog from "../ConfirmDialog";

// Fotografía de ganado para el fondo del encabezado (si falla, queda el degradado).
const BANNER_IMG =
  "https://images.unsplash.com/photo-1560493676-04071c5f467b?auto=format&fit=crop&w=1200&q=60";

export default function AppLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const { activeFarm, activeFarmId, refreshFarms } = useFarm();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [showDelete, setShowDelete] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const userMenuRef = useRef<HTMLDivElement>(null);
  const [deleteStep, setDeleteStep] = useState<1 | 2>(1);
  const [confirmText, setConfirmText] = useState("");
  const [delLoading, setDelLoading] = useState(false);
  const [delError, setDelError] = useState("");

  const [bannerOk, setBannerOk] = useState(true);
  const [farmEditing, setFarmEditing] = useState(false);
  const [farmEditStep, setFarmEditStep] = useState(0);
  const [departments, setDepartments] = useState<DepartmentOption[]>([]);
  const [purposes, setPurposes] = useState<PurposeOption[]>([]);
  const [farmEditForm, setFarmEditForm] = useState<FarmRequest | null>(null);
  const [farmSaving, setFarmSaving] = useState(false);
  const [farmActionError, setFarmActionError] = useState("");
  const [showFarmDelete, setShowFarmDelete] = useState(false);
  const [farmDeleting, setFarmDeleting] = useState(false);

  const isOwner = activeFarm ? activeFarm.owner_id === user?.id : false;

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

  const nextEditStep = () => setFarmEditStep((s) => Math.min(s + 1, 1));
  const prevEditStep = () => setFarmEditStep((s) => Math.max(s - 1, 0));

  const handleStartEdit = async () => {
    if (!activeFarm) return;
    setFarmActionError("");
    const [deps, purps] = await Promise.all([listDepartments(), listPurposes()]);
    setDepartments(deps);
    setPurposes(purps);
    setFarmEditForm({
      name: activeFarm.name,
      address: activeFarm.address,
      department_id: activeFarm.department_id,
      city_municipality: activeFarm.city_municipality,
      total_area: activeFarm.total_area,
      area_unit: activeFarm.area_unit,
      purpose_id: activeFarm.purpose_id,
      farm_identifier: activeFarm.farm_identifier,
      phone: activeFarm.phone,
    });
    setFarmEditStep(0);
    setFarmEditing(true);
    setUserMenuOpen(false);
  };

  const handleSaveFarmEdit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeFarmId || !farmEditForm) return;
    setFarmSaving(true);
    setFarmActionError("");
    try {
      await updateFarm(activeFarmId, farmEditForm);
      await refreshFarms();
      setFarmEditing(false);
    } catch (err: unknown) {
      setFarmActionError(err instanceof Error ? err.message : "No se pudo actualizar la finca");
    } finally {
      setFarmSaving(false);
    }
  };

  const handleDeleteFarm = async () => {
    if (!activeFarmId) return;
    setFarmDeleting(true);
    try {
      await deleteFarm(activeFarmId);
      setShowFarmDelete(false);
      await refreshFarms();
    } catch (err: unknown) {
      setFarmActionError(err instanceof Error ? err.message : "No se pudo eliminar la finca");
    } finally {
      setFarmDeleting(false);
    }
  };

  useEffect(() => {
    if (!userMenuOpen) return;
    const onPointerDown = (e: PointerEvent) => {
      if (userMenuRef.current && !userMenuRef.current.contains(e.target as Node)) {
        setUserMenuOpen(false);
      }
    };
    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") setUserMenuOpen(false);
    };
    document.addEventListener("pointerdown", onPointerDown);
    document.addEventListener("keydown", onKeyDown);
    return () => {
      document.removeEventListener("pointerdown", onPointerDown);
      document.removeEventListener("keydown", onKeyDown);
    };
  }, [userMenuOpen]);

  return (
    <div className="flex min-h-screen bg-background">
      <SessionGuard />
      <Sidebar
        open={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />

      <div className="flex min-w-0 flex-1 flex-col">
        {/* Navbar: banner con la finca activa */}
        <header className="sticky top-0 z-30 border-b-2 border-primary-light">
          <div className="relative bg-gradient-to-br from-primary/20 via-cream to-accent/30">
            {bannerOk && (
              <img
                src={BANNER_IMG}
                alt=""
                onError={() => setBannerOk(false)}
                className="absolute inset-0 h-full w-full object-cover opacity-80"
              />
            )}
            <div className="absolute inset-0 bg-gradient-to-b from-white/30 via-white/5 to-background/30" />
            <div className="relative z-10 flex h-20 items-center gap-3 px-4">
              <button
                onClick={() => setSidebarOpen((v) => !v)}
                className="rounded-lg p-2 text-text-secondary transition-colors hover:bg-surface-alt lg:hidden"
                aria-label="Abrir menú"
              >
                <Menu size={22} />
              </button>

              <ThemeToggle />

              <Tractor size={22} className="shrink-0 text-primary" />

              <div className="min-w-0 leading-tight">
                <p className="truncate text-[10px] font-semibold uppercase tracking-wide text-text-primary">
                  Bienvenido, {user?.first_name}
                </p>
                <h1 className="truncate text-base font-bold text-text-primary">
                  {activeFarm ? activeFarm.name : "BoviTrack"}
                </h1>
                {activeFarm && (
                  <p className="truncate text-xs text-text-primary">
                    {activeFarm.city_municipality} · {activeFarm.total_area} {activeFarm.area_unit}
                  </p>
                )}
              </div>

              <div className="relative ml-auto" ref={userMenuRef}>
                  <button
                    onClick={() => setUserMenuOpen((v) => !v)}
                    title={`${user?.first_name} ${user?.last_name}`}
                    aria-label="Menú de usuario"
                    aria-expanded={userMenuOpen}
                    className={`flex h-9 w-9 items-center justify-center rounded-full text-white transition-transform hover:scale-105 ${userMenuOpen ? "bg-primary-light" : "bg-primary"}`}
                  >
                    <svg
                      viewBox="0 0 448 512"
                      className="h-5 w-auto"
                      fill="currentColor"
                      aria-hidden="true"
                    >
                      <path d="M224 256A128 128 0 1 0 224 0a128 128 0 1 0 0 256zm-45.7 48C79.8 304 0 383.8 0 482.3C0 498.7 13.3 512 29.7 512l388.6 0c16.4 0 29.7-13.3 29.7-29.7C448 383.8 368.2 304 269.7 304l-91.4 0z" />
                    </svg>
                  </button>

                  {userMenuOpen && (
                    <div className="absolute right-0 top-12 z-50 w-60 overflow-hidden rounded-xl border border-border bg-surface shadow-lg">
                      <div className="border-b border-border bg-surface-alt/50 px-4 py-3">
                        <p className="truncate text-sm font-medium text-text-primary">
                          {user?.first_name} {user?.last_name}
                        </p>
                        {user?.role_name && (
                          <p className="text-xs uppercase tracking-wide text-text-muted">{user.role_name}</p>
                        )}
                      </div>
                      <div className="p-1.5">
                        {isOwner && (
                          <>
                            <button
                              onClick={handleStartEdit}
                              className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-left text-sm font-medium text-text-secondary transition-colors hover:bg-surface-alt hover:text-text-primary"
                            >
                              <Pencil size={16} className="text-primary" /> Editar finca
                            </button>
                            <button
                              onClick={() => { setUserMenuOpen(false); setShowFarmDelete(true); }}
                              className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-left text-sm font-medium text-red-600 transition-colors hover:bg-red-50"
                            >
                              <Trash2 size={16} /> Eliminar finca
                            </button>
                          </>
                        )}
                        {(!user?.role_name || user.role_name === "Administrador") && (
                          <button
                            onClick={() => { setUserMenuOpen(false); navigate("/farms/new"); }}
                            className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-left text-sm font-medium text-text-secondary transition-colors hover:bg-surface-alt hover:text-text-primary"
                          >
                            <Plus size={16} className="text-primary" /> Crear finca
                          </button>
                        )}
                        <div className="my-1.5 h-px bg-border" />
                        <button
                          onClick={() => {
                            setUserMenuOpen(false);
                            logout();
                            navigate("/login");
                          }}
                          className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-left text-sm font-medium text-text-secondary transition-colors hover:bg-surface-alt hover:text-text-primary"
                        >
                          <LogOut size={16} className="text-primary" /> Salir
                        </button>
                        <button
                          onClick={() => {
                            setUserMenuOpen(false);
                            setShowDelete(true);
                          }}
                          className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-left text-sm font-medium text-red-600 transition-colors hover:bg-red-50"
                        >
                          <Trash2 size={16} /> Eliminar cuenta
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
        </header>

        {/* Formulario de edición de la finca (2 pasos) */}
        {farmEditing && farmEditForm && (
          <div className="mx-auto w-full max-w-6xl px-4 pt-4">
            {farmActionError && (
              <div className="mb-3 rounded-lg bg-red-50 px-4 py-2 text-sm text-red-700">{farmActionError}</div>
            )}
            <form onSubmit={handleSaveFarmEdit} className="rounded-2xl border border-border bg-surface p-4 shadow-sm">
              <h3 className="mb-3 text-sm font-bold text-text-secondary">Editar finca</h3>
              <div className="mb-4 flex items-center gap-1.5">
                {["Ubicación", "Área y ID"].map((label, i) => (
                  <button key={i} type="button" onClick={() => { if (i < farmEditStep) setFarmEditStep(i); }} disabled={i > farmEditStep}
                    className={`flex-1 rounded-lg px-2 py-1.5 text-center text-xs font-semibold transition-colors ${i === farmEditStep ? "bg-primary text-white" : i < farmEditStep ? "bg-green-100 text-green-700" : "bg-surface-alt text-text-muted cursor-default"}`}
                  >
                    {i < farmEditStep ? "✓ " : ""}{label}
                  </button>
                ))}
              </div>
              {farmEditStep === 0 && (
                <div className="grid gap-3 sm:grid-cols-2">
                  <div>
                    <label className="mb-1 block text-xs font-medium text-text-secondary">Nombre</label>
                    <input type="text" value={farmEditForm.name} onChange={(e) => setFarmEditForm({ ...farmEditForm, name: e.target.value })}
                      className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none" required />
                  </div>
                  <div>
                    <label className="mb-1 block text-xs font-medium text-text-secondary">Dirección</label>
                    <input type="text" value={farmEditForm.address} onChange={(e) => setFarmEditForm({ ...farmEditForm, address: e.target.value })}
                      className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none" required />
                  </div>
                  <div>
                    <label className="mb-1 block text-xs font-medium text-text-secondary">Departamento</label>
                    <select value={farmEditForm.department_id} onChange={(e) => setFarmEditForm({ ...farmEditForm, department_id: e.target.value })}
                      className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none">
                      {departments.map((d) => <option key={d.id} value={d.id}>{d.name}</option>)}
                    </select>
                  </div>
                  <div>
                    <label className="mb-1 block text-xs font-medium text-text-secondary">Ciudad / Municipio</label>
                    <input type="text" value={farmEditForm.city_municipality} onChange={(e) => setFarmEditForm({ ...farmEditForm, city_municipality: e.target.value })}
                      className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none" required />
                  </div>
                </div>
              )}
              {farmEditStep === 1 && (
                <div className="grid gap-3 sm:grid-cols-2">
                  <div>
                    <label className="mb-1 block text-xs font-medium text-text-secondary">Área total</label>
                    <input type="number" min={0.01} step={0.01} value={farmEditForm.total_area}
                      onChange={(e) => setFarmEditForm({ ...farmEditForm, total_area: parseFloat(e.target.value) })}
                      className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none" required />
                  </div>
                  <div>
                    <label className="mb-1 block text-xs font-medium text-text-secondary">Propósito</label>
                    <select value={farmEditForm.purpose_id} onChange={(e) => setFarmEditForm({ ...farmEditForm, purpose_id: e.target.value })}
                      className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none">
                      {purposes.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
                    </select>
                  </div>
                  <div>
                    <label className="mb-1 block text-xs font-medium text-text-secondary">Identificador</label>
                    <input type="text" value={farmEditForm.farm_identifier} onChange={(e) => setFarmEditForm({ ...farmEditForm, farm_identifier: e.target.value })}
                      className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none" required />
                  </div>
                  <div>
                    <label className="mb-1 block text-xs font-medium text-text-secondary">Teléfono</label>
                    <input type="text" value={farmEditForm.phone ?? ""} onChange={(e) => setFarmEditForm({ ...farmEditForm, phone: e.target.value || null })}
                      className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none" />
                  </div>
                </div>
              )}
              <div className="mt-3 flex gap-2">
                {farmEditStep > 0 && (
                  <button type="button" onClick={prevEditStep}
                    className="rounded-lg border border-border px-4 py-2 text-sm font-medium text-text-secondary hover:bg-surface-alt">
                    ← Anterior
                  </button>
                )}
                {farmEditStep < 1 ? (
                  <button type="button" onClick={nextEditStep}
                    className="rounded-lg bg-primary px-4 py-2 text-sm font-bold text-white hover:bg-primary-light">
                    Siguiente →
                  </button>
                ) : (
                  <>
                    <button type="button" onClick={() => setFarmEditing(false)}
                      className="rounded-lg border border-border px-4 py-2 text-sm font-medium text-text-secondary hover:bg-surface-alt">
                      Cancelar
                    </button>
                    <button type="submit" disabled={farmSaving}
                      className="rounded-lg bg-primary px-4 py-2 text-sm font-bold text-white hover:bg-primary-light disabled:opacity-60">
                      {farmSaving ? "Guardando..." : "Guardar cambios"}
                    </button>
                  </>
                )}
              </div>
            </form>
          </div>
        )}

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
          <Outlet />
        </main>

        {/* Footer */}
        <footer className="border-t border-border bg-surface py-3 text-center text-xs text-text-muted">
          © {new Date().getFullYear()} BoviTrack — Gestión Ganadera Inteligente
        </footer>
      </div>

      <ConfirmDialog
        open={showFarmDelete}
        title="Eliminar finca"
        message={`¿Eliminar la finca "${activeFarm?.name}"? Esta acción la desactivará.`}
        confirmLabel="Eliminar"
        loading={farmDeleting}
        onConfirm={handleDeleteFarm}
        onCancel={() => setShowFarmDelete(false)}
      />
    </div>
  );
}