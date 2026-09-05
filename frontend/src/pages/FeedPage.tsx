import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { PostComposer } from "@/components/PostComposer";
import { PostCard } from "@/components/PostCard";
import { feedApi } from "@/api/feed";
import { Skeleton } from "@/components/ui/skeleton";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export function FeedPage() {
  const [offset, setOffset] = useState(0);
  const limit = 20;
  const [allPosts, setAllPosts] = useState<any[]>([]);

  const query = useQuery({
    queryKey: ["feed", offset],
    queryFn: async () => {
      const data = await feedApi.get(limit, offset);
      if (offset === 0) setAllPosts(data);
      else setAllPosts((prev) => [...prev, ...data]);
      return data;
    },
  });

  const hasMore = query.data?.length === limit;

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div className="rounded-[24px] border bg-card p-6">
        <h1 className="text-xl font-bold">Лента</h1>
        <p className="text-sm text-muted-foreground">Что происходит в IT-сообществе — глобальная лента по времени.</p>
      </div>

      <PostComposer onCreated={() => { setOffset(0); query.refetch(); }} />

      <div className="space-y-4">
        {query.isPending && offset === 0 && <Skeleton className="h-40 w-full rounded-2xl" />}
        {query.isError && (
          <Card>
            <CardContent className="p-6 text-center text-sm text-red-500">Ошибка загрузки ленты</CardContent>
          </Card>
        )}
        {query.isSuccess && allPosts.length === 0 && (
          <Card>
            <CardContent className="p-6 text-center">
              <p className="text-sm font-medium">Лента пуста</p>
              <p className="text-xs text-muted-foreground">Стань первым — создай пост!</p>
            </CardContent>
          </Card>
        )}
        {(allPosts.length > 0 ? allPosts : query.data ?? []).map((p) => (
          <PostCard key={p.id} post={p} onUpdated={() => query.refetch()} withComments={false} />
        ))}
      </div>

      {hasMore && (
        <div className="flex justify-center">
          <Button variant="outline" onClick={() => setOffset((o) => o + limit)} disabled={query.isFetching}>
            {query.isFetching ? "Загрузка..." : "Загрузить ещё"}
          </Button>
        </div>
      )}
    </div>
  );
}
