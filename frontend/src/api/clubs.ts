import { api, API_URL } from "./client";

export type ClubRead = {
  id: string;
  owner_id: string;
  name: string;
  slug: string;
  description: string | null;
  avatar_url: string | null;
  cover_url: string | null;
  created_at: string;
  updated_at: string;
  members_count: number;
  is_member: boolean;
  role: string | null;
};

export const clubsApi = {
  list(q?: string, limit = 20, offset = 0): Promise<ClubRead[]> {
    const params = new URLSearchParams({ limit: String(limit), offset: String(offset) });
    if (q) params.set("q", q);
    return api.get<ClubRead[]>(`/api/v1/clubs?${params.toString()}`);
  },
  get(slug: string): Promise<ClubRead> {
    return api.get<ClubRead>(`/api/v1/clubs/${encodeURIComponent(slug)}`);
  },
  create(name: string, description?: string): Promise<ClubRead> {
    return api.post<ClubRead>(`/api/v1/clubs`, { name, description });
  },
  update(slug: string, data: { name?: string; description?: string }): Promise<ClubRead> {
    return api.patch<ClubRead>(`/api/v1/clubs/${encodeURIComponent(slug)}`, data);
  },
  remove(slug: string): Promise<void> {
    return fetch(`${API_URL}/api/v1/clubs/${encodeURIComponent(slug)}`, { method: "DELETE", credentials: "include" }).then(async (r) => {
      if (!r.ok && r.status !== 204) {
        const d = await r.json().catch(() => ({}));
        throw new Error(d.detail || r.statusText);
      }
    });
  },
  join(slug: string) {
    return fetch(`${API_URL}/api/v1/clubs/${encodeURIComponent(slug)}/join`, { method: "POST", credentials: "include" }).then(async (r) => {
      if (!r.ok) {
        const d = await r.json().catch(() => ({}));
        throw new Error(d.detail || r.statusText);
      }
      return r.json().catch(() => ({}));
    });
  },
  leave(slug: string) {
    return fetch(`${API_URL}/api/v1/clubs/${encodeURIComponent(slug)}/leave`, { method: "DELETE", credentials: "include" }).then(async (r) => {
      if (!r.ok && r.status !== 204) {
        const d = await r.json().catch(() => ({}));
        throw new Error(d.detail || r.statusText);
      }
    });
  },
  members(slug: string, limit = 20, offset = 0): Promise<{ items: { id: string; user_id: string; username: string; display_name: string | null; avatar_url: string | null; role: string; joined_at: string }[]; total: number }> {
    return api.get(`/api/v1/clubs/${encodeURIComponent(slug)}/members?limit=${limit}&offset=${offset}`);
  },
  updateRole(slug: string, username: string, role: string) {
    return api.patch(`/api/v1/clubs/${encodeURIComponent(slug)}/members/${encodeURIComponent(username)}/role`, { role });
  },
  removeMember(slug: string, username: string) {
    return fetch(`${API_URL}/api/v1/clubs/${encodeURIComponent(slug)}/members/${encodeURIComponent(username)}`, { method: "DELETE", credentials: "include" }).then(async (r) => {
      if (!r.ok && r.status !== 204) {
        const d = await r.json().catch(() => ({}));
        throw new Error(d.detail || r.statusText);
      }
    });
  },
  uploadAvatar(slug: string, file: File) {
    const fd = new FormData();
    fd.append("file", file);
    return fetch(`${API_URL}/api/v1/clubs/${encodeURIComponent(slug)}/avatar`, { method: "POST", body: fd, credentials: "include" }).then(async (r) => {
      if (!r.ok) {
        const d = await r.json().catch(() => ({}));
        throw new Error(d.detail || r.statusText);
      }
      return r.json();
    });
  },
  uploadCover(slug: string, file: File) {
    const fd = new FormData();
    fd.append("file", file);
    return fetch(`${API_URL}/api/v1/clubs/${encodeURIComponent(slug)}/cover`, { method: "POST", body: fd, credentials: "include" }).then(async (r) => {
      if (!r.ok) {
        const d = await r.json().catch(() => ({}));
        throw new Error(d.detail || r.statusText);
      }
      return r.json();
    });
  },
};
