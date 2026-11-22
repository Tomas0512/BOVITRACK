/*
 * features/identity/identity.test.tsx
 * ¿Qué?  Pruebas de los guards de rutas, del contrato del cliente HTTP de identidad
 *        y de la API pública de la feature.
 * ¿Para? Que ninguna pantalla privada se vea sin sesión y que las llamadas
 *        coincidan con el backend (módulo identity).
 */

import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import type { ReactNode } from "react";

import type { AuthContextType } from "./types";
import { AuthContext } from "./session/authContextDef";
import ProtectedRoute from "./components/ProtectedRoute";
import RequireRole from "./components/RequireRole";

vi.mock("@/core/http", () => ({
  http: { get: vi.fn(), post: vi.fn(), delete: vi.fn() },
}));

import { http } from "@/core/http";
import { deleteAccount, forgotPassword, loginUser, verifyEmail } from "./api";

const mocked = vi.mocked(http, true);
beforeEach(() => vi.clearAllMocks());

function session(overrides: Partial<AuthContextType>): AuthContextType {
  return {
    user: null, accessToken: null, refreshToken: null, isAuthenticated: false, isLoading: false,
    login: vi.fn(), register: vi.fn(), logout: vi.fn(), forgotPassword: vi.fn(), resetPassword: vi.fn(),
    ...overrides,
  } as AuthContextType;
}

function renderAt(path: string, value: AuthContextType, guarded: ReactNode) {
  return render(
    <AuthContext.Provider value={value}>
      <MemoryRouter initialEntries={[path]}>
        <Routes>
          <Route path="/login" element={<p>pantalla de login</p>} />
          <Route path="/dashboard" element={<p>dashboard</p>} />
          <Route path="/privada" element={guarded} />
        </Routes>
      </MemoryRouter>
    </AuthContext.Provider>,
  );
}

describe("features/identity · guards", () => {
  it("ProtectedRoute manda al login si no hay sesión", () => {
    renderAt("/privada", session({}), <ProtectedRoute><p>secreto</p></ProtectedRoute>);
    expect(screen.getByText("pantalla de login")).toBeInTheDocument();
    expect(screen.queryByText("secreto")).not.toBeInTheDocument();
  });

  it("ProtectedRoute no decide mientras la sesión carga, y deja pasar con sesión", () => {
    const { unmount } = renderAt("/privada", session({ isLoading: true }), <ProtectedRoute><p>secreto</p></ProtectedRoute>);
    expect(screen.queryByText("pantalla de login")).not.toBeInTheDocument();
    expect(screen.queryByText("secreto")).not.toBeInTheDocument();
    unmount();

    renderAt("/privada", session({ isAuthenticated: true }), <ProtectedRoute><p>secreto</p></ProtectedRoute>);
    expect(screen.getByText("secreto")).toBeInTheDocument();
  });

  it("RequireRole solo deja pasar al rol indicado", () => {
    const admin = session({ isAuthenticated: true, user: { role_name: "Administrador" } as AuthContextType["user"] });
    const { unmount } = renderAt("/privada", admin, <RequireRole role="Administrador"><p>auditoría</p></RequireRole>);
    expect(screen.getByText("auditoría")).toBeInTheDocument();
    unmount();

    const empleado = session({ isAuthenticated: true, user: { role_name: "Empleado" } as AuthContextType["user"] });
    renderAt("/privada", empleado, <RequireRole role="Administrador"><p>auditoría</p></RequireRole>);
    expect(screen.getByText("dashboard")).toBeInTheDocument();
  });
});

describe("features/identity · api", () => {
  it("usa las rutas del módulo identity del backend", async () => {
    mocked.post.mockResolvedValue({ data: {} });
    mocked.delete.mockResolvedValue({ data: {} });

    await loginUser({ email: "a@x.com", password: "x" });
    await forgotPassword("a@x.com");
    await verifyEmail("tok");
    await deleteAccount();

    expect(mocked.post.mock.calls.map((c) => c[0])).toEqual(["/auth/login", "/auth/forgot-password", "/auth/verify-email"]);
    expect(mocked.post.mock.calls[2][2]).toEqual({ params: { token: "tok" } });
    // borrar la cuenta exige escribir ELIMINAR (lo valida el backend)
    expect(mocked.delete).toHaveBeenCalledWith("/users/me", { data: { confirmation_text: "ELIMINAR" } });
  });
});

describe("features/identity · API pública", () => {
  it("expone la sesión, los guards, las pantallas de acceso y la baja de cuenta", async () => {
    const publicApi = await import("./index");

    expect(Object.keys(publicApi).sort()).toEqual([
      "AuthProvider", "ForgotPasswordPage", "LoginPage", "ProtectedRoute", "RegisterPage", "RequireRole",
      "ResetPasswordPage", "SessionGuard", "VerifyEmailPage", "deleteAccount", "useAuth",
    ]);
  });
});
