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

export const authApi = {
  me(): Promise<UserRead> {
    return api.get<UserRead>("/api/v1/auth/me");
  },
  register(payload: { username: string; email: string; password: string; display_name?: string }): Promise<UserRead> {
    return api.post<UserRead>("/api/v1/auth/register", payload);
  },
  login(payload: { identifier: string; password: string }): Promise<UserRead> {
    return api.post<UserRead>("/api/v1/auth/login", payload);
  },
  logout(): Promise<void> {
    return api.post<void>("/api/v1/auth/logout", {});
  },
};
