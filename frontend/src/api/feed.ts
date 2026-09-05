import { api } from "./client";
import { PostRead } from "./posts";

export const feedApi = {
  get(limit = 20, offset = 0): Promise<PostRead[]> {
    return api.get<PostRead[]>(`/api/v1/feed?limit=${limit}&offset=${offset}`);
  },
};
