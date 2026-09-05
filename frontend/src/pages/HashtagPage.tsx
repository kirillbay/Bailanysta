import { useParams, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { searchApi } from "@/api/search";
import { PostCard } from "@/components/PostCard";
import { Skeleton } from "@/components/ui/skeleton";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useState } from "react";

export function HashtagPage() {
  const { name } = useParams();
  const clean = (name || "").replace(/^#/, "").toLowerCase();
  const [offset, setOffset] = useState(0);
  const [all, setAll] = useState<any[]>([]);
  const limit = 20;

  const infoQuery = useQuery({
    queryKey: ["hashtag", clean],
    queryFn: () => searchApi.hashtag(clean),
    enabled: !!clean,
  });

  const postsQuery = useQuery({
    queryKey: ["hashtag-posts", clean, offset],
    queryFn: async () => {
      const data = await searchApi.hashtagPosts(clean, limit, offset);
      if (offset === 0) setAll(data);
      else setAll((prev) => [...prev, ...data]);
      return data;
    },
    enabled: !!clean,
  });

  const posts = all.length > 0 ? all : postsQuery.data ?? [];

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div className="rounded-2xl border bg-card p-6">
        <h1 className="text-xl font-bold">#{clean}</h1>
        {infoQuery.isPending ? (
          <Skeleton className="h-4 w-32 mt-2" />
        ) : infoQuery.isError ? (
          <p className="text-sm text-red-500">Хештег не найден</p>
        ) : (
          <p className="text-sm text-muted-foreground">{infoQuery.data?.posts_count ?? 0} постов</p>
        )}
      </div>

      {postsQuery.isPending && offset === 0 && <Skeleton className="h-40 w-full rounded-2xl" />}
      {postsQuery.isError && (
        <Card>
          <CardContent className="p-6 text-center text-sm text-red-500">Ошибка загрузки</CardContent>
        </Card>
      )}
      {postsQuery.isSuccess && posts.length === 0 && (
        <Card>
          <CardContent className="p-6 text-center text-sm text-muted-foreground">Пока нет постов с этим хештегом</CardContent>
        </Card>
      )}
      {posts.map((p: any) => (
        <PostCard key={p.id} post={p} onUpdated={() => postsQuery.refetch()} />
      ))}
      {postsQuery.data?.length === limit && (
        <div className="flex justify-center">
          <Button variant="outline" onClick={() => setOffset((o) => o + limit)} disabled={postsQuery.isFetching}>
            Загрузить ещё
          </Button>
        </div>
      )}
      <div className="text-center">
        <Link to="/search" className="text-xs text-muted-foreground hover:underline">← К поиску</Link>
      </div>
    </div>
  );
}
