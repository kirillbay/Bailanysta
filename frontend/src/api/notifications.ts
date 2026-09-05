import { api } from "./client";

export type NotificationRead = {
  id: string;
  recipient_id: string;
  actor_id: string | null;
  actor: { id: string; username: string; display_name: string | null; avatar_url: string | null } | null;
  type: string;
  title: string | null;
  message: string | null;
  entity_type: string | null;
  entity_id: string | null;
  is_read: boolean;
  created_at: string;
};

export const notificationsApi = {
  list(limit = 20, offset = 0, unread_only = false): Promise<NotificationRead[]> {
    return api.get<NotificationRead[]>(`/api/v1/notifications?limit=${limit}&offset=${offset}&unread_only=${unread_only}`);
  },
  unreadCount(): Promise<{ count: number }> {
    return api.get<{ count: number }>("/api/v1/notifications/unread-count");
  },
  markRead(id: string): Promise<NotificationRead> {
    return api.patch<NotificationRead>(`/api/v1/notifications/${id}/read`, {});
  },
  markAllRead(): Promise<{ detail: string }> {
    return api.post<{ detail: string }>("/api/v1/notifications/read-all", {});
  },
  remove(id: string): Promise<void> {
    return fetch(`${import.meta.env.VITE_API_URL ?? "http://localhost:8000"}/api/v1/notifications/${id}`, { method: "DELETE", credentials: "include" }).then(async (r) => {
      if (!r.ok && r.status !== 204) {
        const d = await r.json().catch(() => ({}));
        throw new Error(d.detail || r.statusText);
      }
    });
  },
};
