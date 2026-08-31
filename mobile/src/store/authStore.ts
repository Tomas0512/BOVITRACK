import { create } from 'zustand';
import {
  setAuthToken,
  loadAuthStorage,
  saveAuthStorage,
  clearAuthStorage,
  onLogoutEvent,
} from '../services/api';
import type { UserResponse, TokenResponse } from '../types/auth';

interface AuthState {
  user: UserResponse | null;
  accessToken: string | null;
  loading: boolean;
  login: (tokens: TokenResponse, user: UserResponse) => Promise<void>;
  logout: () => Promise<void>;
  hydrate: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => {
  const doLogout = async () => {
    await clearAuthStorage();
    setAuthToken(null);
    set({ user: null, accessToken: null });
  };

  // Si el interceptor falla el refresh (sesión inválida), cerramos sesión.
  onLogoutEvent(() => { void doLogout(); });

  return {
    user: null,
    accessToken: null,
    loading: true,

    login: async (tokens, user) => {
      await saveAuthStorage(tokens.access_token, tokens.refresh_token);
      setAuthToken(tokens.access_token);
      set({ user, accessToken: tokens.access_token });
    },

    logout: async () => {
      await doLogout();
    },

    hydrate: async () => {
      const { access } = await loadAuthStorage();
      if (access) setAuthToken(access);
      set({ accessToken: access, loading: false });
    },
  };
});
