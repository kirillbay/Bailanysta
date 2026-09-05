import { API_URL } from "./client";

export type StoryRead = {
  id: string;
  author_id: string;
  author: { id: string; username: string; display_name: string | null; avatar_url: string | null } | null;
  media_url: string | null;
  media_type: string | null;
  text: string | null;
  created_at: string;
  expires_at: string;
};

export type StoryGroup = { author: StoryRead["author"]; stories: StoryRead[] };

export const storiesApi = {
  list(): Promise<StoryGroup[]> {
    return fetch(`${API_URL}/api/v1/stories`, { credentials: "include" }).then(async (r) => {
      if (!r.ok) {
        const d = await r.json().catch(() => ({}));
        throw new Error(d.detail || r.statusText);
      }
      return r.json();
    });
  },
  create(file: File, text?: string): Promise<StoryRead> {
    const fd = new FormData();
    fd.append("file", file);
    if (text) fd.append("text", text);
    return fetch(`${API_URL}/api/v1/stories`, { method: "POST", body: fd, credentials: "include" }).then(async (r) => {
      if (!r.ok) {
        const d = await r.json().catch(() => ({}));
        throw new Error(d.detail || r.statusText);
      }
      return r.json();
    });
  },
  get(id: string): Promise<StoryRead> {
    return fetch(`${API_URL}/api/v1/stories/${id}`, { credentials: "include" }).then(async (r) => {
      if (!r.ok) {
        const d = await r.json().catch(() => ({}));
        throw new Error(d.detail || r.statusText);
      }
      return r.json();
    });
  },
  remove(id: string): Promise<void> {
    return fetch(`${API_URL}/api/v1/stories/${id}`, { method: "DELETE", credentials: "include" }).then(async (r) => {
      if (!r.ok && r.status !== 204) {
        const d = await r.json().catch(() => ({}));
        throw new Error(d.detail || r.statusText);
      }
    });
  },
  resolveUrl(url: string | null) {
    if (!url) return null;
    if (url.startsWith("http")) return url;
    return `${API_URL}${url}`;
  },
};
