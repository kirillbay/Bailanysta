import { api, API_URL } from "./client";

export type UserPublic = {
  id: string;
  username: string;
  display_name: string | null;
  bio: string | null;
  avatar_url: string | null;
  cover_url: string | null;
  created_at: string;
};

export type UserMe = {
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

function resolveUrl(url: string | null): string | null {
  if (!url) return null;
  if (url.startsWith("http")) return url;
  // uploads are served from backend
  return `${API_URL}${url}`;
}

export const usersApi = {
  me(): Promise<UserMe> {
    return api.get<UserMe>("/api/v1/users/me");
  },
  public(username: string): Promise<UserPublic> {
    return api.get<UserPublic>(`/api/v1/users/${encodeURIComponent(username)}`);
  },
  update(data: { display_name?: string | null; bio?: string | null }): Promise<UserMe> {
    return api.patch<UserMe>("/api/v1/users/me", data);
  },
  async uploadAvatar(file: File): Promise<UserMe> {
    const fd = new FormData();
    fd.append("file", file);
    const res = await fetch(`${API_URL}/api/v1/users/me/avatar`, {
      method: "POST",
      body: fd,
      credentials: "include",
    });
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      throw new Error(data.detail || res.statusText);
    }
    return res.json();
  },
  async uploadCover(file: File): Promise<UserMe> {
    const fd = new FormData();
    fd.append("file", file);
    const res = await fetch(`${API_URL}/api/v1/users/me/cover`, {
      method: "POST",
      body: fd,
      credentials: "include",
    });
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      throw new Error(data.detail || res.statusText);
    }
    return res.json();
  },
  resolveUrl,
};
