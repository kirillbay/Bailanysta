import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { notificationsApi } from "@/api/notifications";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";
import { Skeleton } from "@/components/ui/skeleton";

export function NotificationsPage() {
  const qc = useQueryClient();
  const query = useQuery({ queryKey: ["notifications"], queryFn: () => notificationsApi.list(50, 0) });
  const unread = useQuery({ queryKey: ["notifications-unread"], queryFn: () => notificationsApi.unreadCount() });

  const markRead = useMutation({
    mutationFn: (id: string) => notificationsApi.markRead(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["notifications"] });
      qc.invalidateQueries({ queryKey: ["notifications-unread"] });
    },
  });
  const markAll = useMutation({
    mutationFn: () => notificationsApi.markAllRead(),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["notifications"] });
      qc.invalidateQueries({ queryKey: ["notifications-unread"] });
    },
  });

  return (
    <div className="mx-auto max-w-2xl space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold">Уведомления {unread.data ? `(${unread.data.count})` : ""}</h1>
        <Button variant="outline" size="sm" onClick={() => markAll.mutate()} disabled={markAll.isPending}>Прочитать все</Button>
      </div>

      {query.isPending && <Skeleton className="h-32 w-full rounded-2xl" />}
      {query.isError && <p className="text-sm text-red-500">Ошибка загрузки</p>}
      {query.isSuccess && query.data.length === 0 && (
        <Card>
          <CardContent className="p-6 text-center text-sm text-muted-foreground">Пока нет уведомлений</CardContent>
        </Card>
      )}
      {query.data?.map((n) => (
        <Card key={n.id} className={n.is_read ? "opacity-60" : ""}>
          <CardContent className="p-4 flex gap-3">
            <div className="h-9 w-9 rounded-full bg-foreground text-background flex items-center justify-center text-xs font-bold shrink-0">
              {n.actor?.username.slice(0, 1).toUpperCase() ?? "•"}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium">{n.title}</p>
              <p className="text-xs text-muted-foreground">{n.message}</p>
              <p className="text-[11px] text-muted-foreground">{new Date(n.created_at).toLocaleString("ru-RU")} · {n.type}</p>
              {n.entity_type === "post" && n.entity_id && (
                <Link to={`/posts/${n.entity_id}`} className="text-xs text-primary hover:underline">Открыть пост</Link>
              )}
              {n.entity_type === "user" && n.actor && (
                <Link to={`/profile/${n.actor.username}`} className="text-xs text-primary hover:underline">Профиль</Link>
              )}
            </div>
            <div className="flex flex-col gap-1">
              {!n.is_read && (
                <Button size="sm" variant="ghost" onClick={() => markRead.mutate(n.id)}>
                  Прочитать
                </Button>
              )}
              <Button variant="ghost" size="sm" onClick={() => notificationsApi.remove(n.id).then(() => qc.invalidateQueries({ queryKey: ["notifications"] }))}>
                Удалить
              </Button>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
