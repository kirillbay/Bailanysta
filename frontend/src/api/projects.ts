import { api, API_URL } from "./client";

export type ProjectOwner = {
  id: string;
  username: string;
  display_name: string | null;
  avatar_url: string | null;
};

export type ProjectRead = {
  id: string;
  owner_id: string;
  owner: ProjectOwner | null;
  name: string;
  description: string;
  technologies: string[];
  github_url: string | null;
  demo_url: string | null;
  image_url: string | null;
  status: "idea" | "in_progress" | "completed" | "archived";
  position: number;
  created_at: string;
  updated_at: string;
};

function resolveImage(url: string | null): string | null {
  if (!url) return null;
  if (url.startsWith("http")) return url;
  return `${API_URL}${url}`;
}

export const projectsApi = {
  listUser(username: string, params?: { limit?: number; offset?: number }): Promise<ProjectRead[]> {
    const q = new URLSearchParams();
    if (params?.limit) q.set("limit", String(params.limit));
    if (params?.offset) q.set("offset", String(params.offset));
    const qs = q.toString() ? `?${q}` : "";
    return api.get<ProjectRead[]>(`/api/v1/users/${encodeURIComponent(username)}/projects${qs}`);
  },
  listMy(params?: { limit?: number; offset?: number }): Promise<ProjectRead[]> {
    const q = new URLSearchParams();
    if (params?.limit) q.set("limit", String(params.limit));
    if (params?.offset) q.set("offset", String(params.offset));
    const qs = q.toString() ? `?${q}` : "";
    return api.get<ProjectRead[]>(`/api/v1/users/me/projects${qs}`);
  },
  get(id: string): Promise<ProjectRead> {
    return api.get<ProjectRead>(`/api/v1/projects/${id}`);
  },
  create(data: { name: string; description: string; technologies: string[]; github_url?: string | null; demo_url?: string | null; status: string }): Promise<ProjectRead> {
    return api.post<ProjectRead>("/api/v1/users/me/projects", data);
  },
  update(id: string, data: Partial<{ name: string; description: string; technologies: string[]; github_url: string | null; demo_url: string | null; status: string }>): Promise<ProjectRead> {
    return api.patch<ProjectRead>(`/api/v1/users/me/projects/${id}`, data);
  },
  async delete(id: string): Promise<void> {
    const res = await fetch(`${API_URL}/api/v1/users/me/projects/${id}`, { method: "DELETE", credentials: "include" });
    if (!res.ok) {
      let detail = res.statusText;
      try { const d = await res.json(); detail = d.detail ?? detail; } catch {}
      throw new Error(detail);
    }
  },
  async uploadImage(id: string, file: File): Promise<ProjectRead> {
    const fd = new FormData();
    fd.append("file", file);
    const res = await fetch(`${API_URL}/api/v1/users/me/projects/${id}/image`, { method: "POST", body: fd, credentials: "include" });
    if (!res.ok) {
      let detail = res.statusText;
      try { const d = await res.json(); detail = d.detail ?? detail; } catch {}
      throw new Error(detail);
    }
    return res.json();
  },
  resolveImage,
};
