import { create } from 'zustand';
import { setAuthToken } from '../services/api';
import type { UserResponse, TokenResponse } from '../types/auth';

interface AuthState {
  user: UserResponse | null;
  accessToken: string | null;
  login: (tokens: TokenResponse, user: UserResponse) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  accessToken: null,

  login: (tokens, user) => {
    setAuthToken(tokens.access_token);
    set({ user, accessToken: tokens.access_token });
  },

  logout: () => {
    setAuthToken(null);
    set({ user: null, accessToken: null });
  },
}));