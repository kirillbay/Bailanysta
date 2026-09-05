import { useState } from "react";
import { useTranslation } from "react-i18next";
import { useQuery } from "@tanstack/react-query";
import { PostComposer } from "@/components/PostComposer";
import { PostCard } from "@/components/PostCard";
import { feedApi } from "@/api/feed";
import { Skeleton } from "@/components/ui/skeleton";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { StoryBar } from "@/components/StoryBar";
import { StoryViewer } from "@/components/StoryViewer";
import { StoryGroup } from "@/api/stories";

export function FeedPage() {
  const { t } = useTranslation();
  const [offset, setOffset] = useState(0);
  const limit = 20;
  const [allPosts, setAllPosts] = useState<any[]>([]);
  const [viewer, setViewer] = useState<{ group: StoryGroup; idx: number } | null>(null);

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
        <h1 className="text-xl font-bold">{t("feed.title")}</h1>
        <p className="text-sm text-muted-foreground">{t("feed.subtitle")}</p>
      </div>

      <StoryBar onSelect={(group, idx) => setViewer({ group, idx })} />
      {viewer && <StoryViewer group={viewer.group} startIdx={viewer.idx} onClose={() => setViewer(null)} />}

      <PostComposer onCreated={() => { setOffset(0); query.refetch(); }} />

      <div className="space-y-4">
        {query.isPending && offset === 0 && <Skeleton className="h-40 w-full rounded-2xl" />}
        {query.isError && (
          <Card>
            <CardContent className="p-6 text-center text-sm text-red-500" role="alert">{t("feed.error")}</CardContent>
          </Card>
        )}
        {query.isSuccess && allPosts.length === 0 && (
          <Card>
            <CardContent className="p-6 text-center">
              <p className="text-sm font-medium">{t("feed.empty")}</p>
              <p className="text-xs text-muted-foreground">{t("feed.emptyDesc")}</p>
            </CardContent>
          </Card>
        )}
        {(allPosts.length > 0 ? allPosts : query.data ?? []).map((p) => (
          <PostCard key={p.id} post={p} onUpdated={() => query.refetch()} withComments={false} />
        ))}
      </div>

      {hasMore && (
        <div className="flex justify-center">
          <Button variant="outline" onClick={() => setOffset((o) => o + limit)} disabled={query.isFetching} aria-label={t("common.loadMore")}>
            {query.isFetching ? t("common.loading") : t("feed.loadMore")}
          </Button>
        </div>
      )}
    </div>
  );
}
