import { api, API_URL } from "./client";

export type FollowUser = { id: string; username: string; display_name: string | null; bio: string | null; avatar_url: string | null; created_at: string; followers_count: number; following_count: number };

export const followsApi = {
  follow(username: string) {
    return fetch(`${API_URL}/api/v1/users/${encodeURIComponent(username)}/follow`, { method: "POST", credentials: "include" }).then(async (r) => {
      if (!r.ok) {
        const d = await r.json().catch(() => ({}));
        throw new Error(d.detail || r.statusText);
      }
      return r.json().catch(() => ({}));
    });
  },
  unfollow(username: string) {
    return fetch(`${API_URL}/api/v1/users/${encodeURIComponent(username)}/follow`, { method: "DELETE", credentials: "include" }).then(async (r) => {
      if (!r.ok && r.status !== 204) {
        const d = await r.json().catch(() => ({}));
        throw new Error(d.detail || r.statusText);
      }
    });
  },
  followers(username: string, limit = 20, offset = 0): Promise<{ items: FollowUser[]; total: number }> {
    return api.get<{ items: FollowUser[]; total: number }>(`/api/v1/users/${encodeURIComponent(username)}/followers?limit=${limit}&offset=${offset}`);
  },
  following(username: string, limit = 20, offset = 0): Promise<{ items: FollowUser[]; total: number }> {
    return api.get<{ items: FollowUser[]; total: number }>(`/api/v1/users/${encodeURIComponent(username)}/following?limit=${limit}&offset=${offset}`);
  },
};
