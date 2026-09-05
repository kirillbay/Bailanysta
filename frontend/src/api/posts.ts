import { api, API_URL } from "./client";

export type PostMedia = { id: string; url: string; mime_type: string; position: number };
export type Author = { id: string; username: string; display_name: string | null; avatar_url: string | null };
export type PostRead = {
  id: string;
  author_id: string;
  content: string;
  created_at: string;
  updated_at: string;
  author: Author;
  media: PostMedia[];
  hashtags: string[];
};

export const postsApi = {
  create(content: string, files: File[]): Promise<PostRead> {
    const fd = new FormData();
    fd.append("content", content);
    files.forEach((f) => fd.append("files", f));
    return fetch(`${API_URL}/api/v1/posts`, { method: "POST", body: fd, credentials: "include" }).then(async (r) => {
      if (!r.ok) {
        const data = await r.json().catch(() => ({}));
        throw new Error(data.detail || r.statusText);
      }
      return r.json();
    });
  },
  get(id: string): Promise<PostRead> {
    return api.get<PostRead>(`/api/v1/posts/${id}`);
  },
  userPosts(username: string, limit = 20, offset = 0): Promise<PostRead[]> {
    return api.get<PostRead[]>(`/api/v1/users/${encodeURIComponent(username)}/posts?limit=${limit}&offset=${offset}`);
  },
  update(id: string, content: string): Promise<PostRead> {
    return api.patch<PostRead>(`/api/v1/posts/${id}`, { content });
  },
  remove(id: string): Promise<void> {
    return fetch(`${API_URL}/api/v1/posts/${id}`, { method: "DELETE", credentials: "include" }).then(async (r) => {
      if (!r.ok) {
        const data = await r.json().catch(() => ({}));
        throw new Error(data.detail || r.statusText);
      }
    });
  },
  resolveUrl(url: string) {
    if (!url) return url;
    if (url.startsWith("http")) return url;
    return `${API_URL}${url}`;
  },
};
