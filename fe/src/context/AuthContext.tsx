import { useCallback, useEffect, useMemo, useState, type ReactNode } from "react";
import { AuthContext } from "./authContextDef";
import {
  loginUser,
  registerUser,
  getMe,
  forgotPassword as apiForgotPassword,
  resetPassword as apiResetPassword,
} from "../api/auth";
import type { UserResponse, RegisterRequest } from "../types/auth";

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserResponse | null>(null);
  const [accessToken, setAccessToken] = useState<string | null>(
    () => sessionStorage.getItem("access_token")
  );
  const [refreshToken, setRefreshToken] = useState<string | null>(
    () => sessionStorage.getItem("refresh_token")
  );
  const [isLoading, setIsLoading] = useState(true);

  const isAuthenticated = !!user && !!accessToken;

  const saveTokens = useCallback((access: string, refresh: string) => {
    sessionStorage.setItem("access_token", access);
    sessionStorage.setItem("refresh_token", refresh);
    setAccessToken(access);
    setRefreshToken(refresh);
  }, []);

  const clearSession = useCallback(() => {
    sessionStorage.removeItem("access_token");
    sessionStorage.removeItem("refresh_token");
    setAccessToken(null);
    setRefreshToken(null);
    setUser(null);
  }, []);

  // Verificar sesión existente al montar
  useEffect(() => {
    const verify = async () => {
      if (!accessToken) {
        setIsLoading(false);
        return;
      }
      try {
        const me = await getMe();
        setUser(me);
      } catch {
        clearSession();
      } finally {
        setIsLoading(false);
      }
    };
    verify();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const login = useCallback(async (email: string, password: string) => {
    const tokens = await loginUser({ email, password });
    saveTokens(tokens.access_token, tokens.refresh_token);
    const me = await getMe();
    setUser(me);
  }, [saveTokens]);

  const register = useCallback(async (data: RegisterRequest) => {
    await registerUser(data);
    // Auto-login después de registro
    await login(data.email, data.password);
  }, [login]);

  const logout = useCallback(() => {
    clearSession();
  }, [clearSession]);

  const forgotPassword = useCallback(async (email: string) => {
    const res = await apiForgotPassword(email);
    return res.message;
  }, []);

  const resetPassword = useCallback(async (token: string, newPassword: string) => {
    const res = await apiResetPassword(token, newPassword);
    return res.message;
  }, []);

  const value = useMemo(
    () => ({
      user,
      accessToken,
      refreshToken,
      isLoading,
      isAuthenticated,
      login,
      register,
      logout,
      forgotPassword,
      resetPassword,
    }),
    [user, accessToken, refreshToken, isLoading, isAuthenticated, login, register, logout, forgotPassword, resetPassword]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
