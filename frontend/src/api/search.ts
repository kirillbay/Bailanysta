import { api } from "./client";
import { PostRead } from "./posts";

export type SearchResult = {
  query: string;
  users: { id: string; username: string; display_name: string | null; bio: string | null; avatar_url: string | null; created_at: string; followers_count: number; following_count: number }[];
  posts: PostRead[];
  hashtags: { id: string; name: string; posts_count: number }[];
  projects: { id: string; owner_id: string; name: string; description: string; technologies: string[]; github_url: string | null; demo_url: string | null; image_url: string | null; status: string; created_at: string | null }[];
  clubs: { id: string; name: string; slug: string; description: string; members_count: number; created_at: string | null }[];
};

export const searchApi = {
  search(q: string, type: "all" | "users" | "posts" | "hashtags" | "projects" | "clubs" = "all", limit = 20, offset = 0): Promise<SearchResult> {
    return api.get<SearchResult>(`/api/v1/search?q=${encodeURIComponent(q)}&type=${type}&limit=${limit}&offset=${offset}`);
  },
  hashtag(name: string) {
    return api.get<{ id: string; name: string; posts_count: number; created_at: string }>(`/api/v1/hashtags/${encodeURIComponent(name.replace(/^#/, ""))}`);
  },
  hashtagPosts(name: string, limit = 20, offset = 0): Promise<PostRead[]> {
    return api.get<PostRead[]>(`/api/v1/hashtags/${encodeURIComponent(name.replace(/^#/, ""))}/posts?limit=${limit}&offset=${offset}`);
  },
};
