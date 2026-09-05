import { useQuery } from "@tanstack/react-query";
import { bookmarksApi } from "@/api/bookmarks";
import { PostCard } from "@/components/PostCard";
import { Skeleton } from "@/components/ui/skeleton";
import { Card, CardContent } from "@/components/ui/card";

export function BookmarksPage() {
  const query = useQuery({ queryKey: ["bookmarks"], queryFn: () => bookmarksApi.list(50, 0) });

  return (
    <div className="mx-auto max-w-2xl space-y-4">
      <h1 className="text-xl font-semibold">Сохранённое</h1>
      {query.isPending && <Skeleton className="h-32 w-full rounded-2xl" />}
      {query.isError && <p className="text-sm text-red-500">Ошибка загрузки</p>}
      {query.isSuccess && query.data.length === 0 && (
        <Card>
          <CardContent className="p-6 text-center text-sm text-muted-foreground">Пока ничего не сохранено</CardContent>
        </Card>
      )}
      {query.data?.map((p) => (
        <PostCard key={p.id} post={p} onUpdated={() => query.refetch()} />
      ))}
    </div>
  );
}
