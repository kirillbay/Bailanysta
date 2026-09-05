import { api } from "./client";
import { PostRead } from "./posts";

export const bookmarksApi = {
  list(limit = 20, offset = 0): Promise<PostRead[]> {
    return api.get<PostRead[]>(`/api/v1/bookmarks?limit=${limit}&offset=${offset}`);
  },
};
