import { api } from "./client";

export type UserRead = {
  id: string;
  username: string;
  email: string;
  display_name: string | null;
  bio: string | null;
  avatar_url: string | null;
  cover_url: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
};

type AuthResponse = {
  user: UserRead;
  access_token: string;
  token_type: string;
};

function storeToken(token: string) {
  try {
    localStorage.setItem("access_token", token);
  } catch {}
}

function clearToken() {
  try {
    localStorage.removeItem("access_token");
  } catch {}
}

export const authApi = {
  me(): Promise<UserRead> {
    return api.get<UserRead>("/api/v1/auth/me");
  },
  async register(payload: { username: string; email: string; password: string; display_name?: string }): Promise<UserRead> {
    const res = await api.post<AuthResponse>("/api/v1/auth/register", payload);
    // res may be UserRead (old) or AuthResponse (new) — handle both for backwards compat
    const maybe = res as unknown as AuthResponse;
    if (maybe.access_token) {
      storeToken(maybe.access_token);
      return maybe.user;
    }
    return res as unknown as UserRead;
  },
  async login(payload: { identifier: string; password: string }): Promise<UserRead> {
    const res = await api.post<AuthResponse>("/api/v1/auth/login", payload);
    const maybe = res as unknown as AuthResponse;
    if (maybe.access_token) {
      storeToken(maybe.access_token);
      return maybe.user;
    }
    return res as unknown as UserRead;
  },
  async logout(): Promise<void> {
    try {
      await api.post<void>("/api/v1/auth/logout", {});
    } finally {
      clearToken();
    }
  },
  async demo(): Promise<UserRead> {
    const res = await api.post<AuthResponse>("/api/v1/auth/demo", {});
    const maybe = res as unknown as AuthResponse;
    if (maybe.access_token) {
      storeToken(maybe.access_token);
      return maybe.user;
    }
    return res as unknown as UserRead;
  },
};
