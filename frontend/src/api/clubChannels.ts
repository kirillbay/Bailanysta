import { api, API_URL } from "./client";

export type ChannelRead = { id: string; club_id: string; name: string; slug: string; description: string | null; position: number; created_at: string; updated_at: string };
export type MessageRead = { id: string; channel_id: string; author_id: string; content: string; is_edited: boolean; created_at: string; updated_at: string; author: { id: string; username: string; display_name: string | null; avatar_url: string | null } | null };

export const clubChannelsApi = {
  list(slug: string): Promise<ChannelRead[]> {
    return api.get<ChannelRead[]>(`/api/v1/clubs/${encodeURIComponent(slug)}/channels`);
  },
  get(slug: string, channelSlug: string): Promise<ChannelRead> {
    return api.get<ChannelRead>(`/api/v1/clubs/${encodeURIComponent(slug)}/channels/${encodeURIComponent(channelSlug)}`);
  },
  create(slug: string, name: string, description?: string): Promise<ChannelRead> {
    return api.post<ChannelRead>(`/api/v1/clubs/${encodeURIComponent(slug)}/channels`, { name, description });
  },
  update(slug: string, channelSlug: string, data: { name?: string; description?: string }): Promise<ChannelRead> {
    return api.patch<ChannelRead>(`/api/v1/clubs/${encodeURIComponent(slug)}/channels/${encodeURIComponent(channelSlug)}`, data);
  },
  remove(slug: string, channelSlug: string): Promise<void> {
    return fetch(`${API_URL}/api/v1/clubs/${encodeURIComponent(slug)}/channels/${encodeURIComponent(channelSlug)}`, { method: "DELETE", credentials: "include" }).then(async (r) => {
      if (!r.ok && r.status !== 204) {
        const d = await r.json().catch(() => ({}));
        throw new Error(d.detail || r.statusText);
      }
    });
  },
  messages(slug: string, channelSlug: string, limit = 50, offset = 0): Promise<MessageRead[]> {
    return api.get<MessageRead[]>(`/api/v1/clubs/${encodeURIComponent(slug)}/channels/${encodeURIComponent(channelSlug)}/messages?limit=${limit}&offset=${offset}`);
  },
  send(slug: string, channelSlug: string, content: string): Promise<MessageRead> {
    return api.post<MessageRead>(`/api/v1/clubs/${encodeURIComponent(slug)}/channels/${encodeURIComponent(channelSlug)}/messages`, { content });
  },
  edit(slug: string, channelSlug: string, messageId: string, content: string): Promise<MessageRead> {
    return api.patch<MessageRead>(`/api/v1/clubs/${encodeURIComponent(slug)}/channels/${encodeURIComponent(channelSlug)}/messages/${messageId}`, { content });
  },
  removeMessage(slug: string, channelSlug: string, messageId: string): Promise<void> {
    return fetch(`${API_URL}/api/v1/clubs/${encodeURIComponent(slug)}/channels/${encodeURIComponent(channelSlug)}/messages/${messageId}`, { method: "DELETE", credentials: "include" }).then(async (r) => {
      if (!r.ok && r.status !== 204) {
        const d = await r.json().catch(() => ({}));
        throw new Error(d.detail || r.statusText);
      }
    });
  },
};
