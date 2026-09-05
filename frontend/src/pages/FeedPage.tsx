import { useTranslation } from "react-i18next";
import { useHealth } from "@/hooks/useHealth";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { API_URL } from "@/api/client";
import { Activity, CheckCircle2, AlertTriangle, RefreshCw, Radio } from "lucide-react";
import { PostComposer } from "@/components/PostComposer";
import { PostCard } from "@/components/PostCard";
import { useQuery } from "@tanstack/react-query";
import { postsApi } from "@/api/posts";
import { useAuth } from "@/stores/auth";

export function FeedPage() {
  const { t } = useTranslation();
  const health = useHealth();
  const { user } = useAuth();

  // Show recent posts from current user as simple feed (STEP5: user posts feed)
  const postsQuery = useQuery({
    queryKey: ["user-posts", user?.username],
    queryFn: () => postsApi.userPosts(user!.username, 20, 0),
    enabled: !!user?.username,
  });

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      {/* Hero */}
      <div className="rounded-[24px] border bg-card p-6 sm:p-8">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div className="space-y-2">
            <Badge className="rounded-full">Bailanysta · STEP 5 Posts</Badge>
            <h1 className="text-2xl font-bold tracking-tight sm:text-[28px]">Байланыста болайық</h1>
            <p className="max-w-[44ch] text-sm leading-relaxed text-muted-foreground">
              {t("common.tagline", "Социальная платформа для IT-комьюнити")} — лента, клубы, проекты и общение.
            </p>
          </div>
          <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-foreground text-background text-lg font-bold">
            Б
          </div>
        </div>
      </div>

      <PostComposer />

      {/* User posts feed */}
      <div className="space-y-4">
        <h2 className="text-sm font-semibold">Мои посты</h2>
        {postsQuery.isPending && <Skeleton className="h-32 w-full rounded-2xl" />}
        {postsQuery.isError && (
          <Card>
            <CardContent className="p-6 text-center text-sm text-muted-foreground">Не удалось загрузить посты</CardContent>
          </Card>
        )}
        {postsQuery.isSuccess && postsQuery.data.length === 0 && (
          <Card>
            <CardContent className="p-6 text-center">
              <p className="text-sm font-medium">Пока пусто</p>
              <p className="text-xs text-muted-foreground">Создай первый пост выше.</p>
            </CardContent>
          </Card>
        )}
        {postsQuery.data?.map((p) => (
          <PostCard key={p.id} post={p} onUpdated={() => postsQuery.refetch()} />
        ))}
      </div>

      {/* Health check card — integration demo */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-base">
            <Radio className="h-4 w-4" /> Frontend ↔ Backend
          </CardTitle>
          <CardDescription>
            Проверка связи: <code className="rounded bg-muted px-1.5 py-0.5 text-xs">{API_URL}/api/v1/health</code>
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          {health.isPending && (
            <div className="space-y-2">
              <Skeleton className="h-4 w-3/4" />
              <Skeleton className="h-4 w-1/2" />
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Activity className="h-4 w-4 animate-pulse" /> {t("common.loading", "Загрузка...")}
              </div>
            </div>
          )}

          {health.isError && (
            <div className="rounded-xl border border-amber-200 bg-amber-50 p-4 dark:border-amber-900 dark:bg-amber-950/30">
              <div className="flex items-start gap-3">
                <AlertTriangle className="mt-0.5 h-5 w-5 text-amber-600" />
                <div className="space-y-1">
                  <p className="text-sm font-medium text-amber-900 dark:text-amber-200">Backend недоступен</p>
                  <p className="text-xs text-amber-800/80 dark:text-amber-200/70">
                    {(health.error as Error)?.message ?? t("common.error", "Ошибка")} — убедись что backend запущен на{" "}
                    <code className="rounded bg-amber-100 px-1 py-0.5 dark:bg-amber-900/50">{API_URL}</code>
                  </p>
                </div>
              </div>
              <Button variant="outline" size="sm" className="mt-3" onClick={() => health.refetch()}>
                <RefreshCw className="mr-2 h-3.5 w-3.5" /> {t("common.retry", "Повторить")}
              </Button>
            </div>
          )}

          {health.isSuccess && (
            <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-4 dark:border-emerald-900 dark:bg-emerald-950/30">
              <div className="flex items-center gap-2 text-emerald-700 dark:text-emerald-300">
                <CheckCircle2 className="h-5 w-5" />
                <span className="text-sm font-semibold">Backend на связи</span>
                <Badge className="ml-auto bg-emerald-600 text-white hover:bg-emerald-600">OK</Badge>
              </div>
              <pre className="mt-3 overflow-auto rounded-lg bg-white p-3 text-xs leading-relaxed dark:bg-black/20">
                {JSON.stringify(health.data, null, 2)}
              </pre>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
