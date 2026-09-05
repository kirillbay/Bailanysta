import { api, API_URL } from "./client";

export type CommentRead = {
  id: string;
  post_id: string;
  author_id: string;
  content: string;
  created_at: string;
  updated_at: string;
  author: { id: string; username: string; display_name: string | null; avatar_url: string | null } | null;
};

export const commentsApi = {
  list(postId: string, limit = 20, offset = 0): Promise<CommentRead[]> {
    return api.get<CommentRead[]>(`/api/v1/posts/${postId}/comments?limit=${limit}&offset=${offset}`);
  },
  create(postId: string, content: string): Promise<CommentRead> {
    return api.post<CommentRead>(`/api/v1/posts/${postId}/comments`, { content });
  },
  update(commentId: string, content: string): Promise<CommentRead> {
    return api.patch<CommentRead>(`/api/v1/comments/${commentId}`, { content });
  },
  remove(commentId: string): Promise<void> {
    return fetch(`${API_URL}/api/v1/comments/${commentId}`, { method: "DELETE", credentials: "include" }).then(async (r) => {
      if (!r.ok && r.status !== 204) {
        const data = await r.json().catch(() => ({}));
        throw new Error(data.detail || r.statusText);
      }
    });
  },
};
