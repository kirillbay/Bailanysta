import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { clubsApi } from "@/api/clubs";
import { clubChannelsApi } from "@/api/clubChannels";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useState } from "react";

export function MessagesPage() {
  const clubsQuery = useQuery({ queryKey: ["clubs", "", 0], queryFn: () => clubsApi.list(undefined, 50, 0) });

  // For each club, fetch channels
  const [selectedClub, setSelectedClub] = useState<string | null>(null);

  const channelsQuery = useQuery({
    queryKey: ["club-channels", selectedClub],
    queryFn: () => clubChannelsApi.list(selectedClub!),
    enabled: !!selectedClub,
  });

  if (clubsQuery.isPending) {
    return <div className="mx-auto max-w-6xl p-6"><Skeleton className="h-64 w-full rounded-2xl" /></div>;
  }

  if (clubsQuery.isError) {
    return <div className="mx-auto max-w-6xl p-6 text-center text-sm text-red-500">Ошибка загрузки клубов</div>;
  }

  const clubs = clubsQuery.data ?? [];

  if (clubs.length === 0) {
    return (
      <div className="mx-auto max-w-2xl space-y-6">
        <h1 className="text-xl font-semibold">Сообщения</h1>
        <Card>
          <CardContent className="p-6 text-center space-y-2">
            <p className="text-sm font-medium">Каналы клубов</p>
            <p className="text-xs text-muted-foreground">Вступи в клуб, чтобы увидеть его каналы. Личные сообщения скоро.</p>
            <Link to="/clubs" className="inline-block rounded-xl bg-foreground px-4 py-2 text-sm text-background">Найти клубы</Link>
          </CardContent>
        </Card>
        <Card className="border-dashed">
          <CardContent className="p-4 text-center text-xs text-muted-foreground">
            Личные сообщения — скоро
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-6xl space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold">Сообщения</h1>
        <span className="text-xs text-muted-foreground">Каналы клубов</span>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-[280px_1fr] gap-6">
        {/* Conversations list */}
        <Card className="overflow-hidden h-fit">
          <CardHeader className="p-4 pb-2">
            <CardTitle className="text-sm">Клубы</CardTitle>
          </CardHeader>
          <CardContent className="p-2 space-y-1">
            {clubs.map((c) => (
              <button
                key={c.slug}
                onClick={() => setSelectedClub(c.slug)}
                className={`w-full text-left rounded-xl px-3 py-2 text-sm hover:bg-accent ${selectedClub === c.slug ? "bg-foreground text-background" : "bg-card border"}`}
              >
                <div className="font-medium truncate">{c.name}</div>
                <div className="text-xs text-muted-foreground truncate">/{c.slug} · {c.members_count ?? 0} участников</div>
              </button>
            ))}
          </CardContent>
        </Card>

        {/* Channel / messages */}
        <Card className="min-h-[400px]">
          {!selectedClub ? (
            <CardContent className="p-6 text-center text-sm text-muted-foreground">
              Выбери клуб слева, чтобы увидеть его каналы
            </CardContent>
          ) : channelsQuery.isPending ? (
            <CardContent className="p-6"><Skeleton className="h-32 w-full" /></CardContent>
          ) : channelsQuery.isError ? (
            <CardContent className="p-6 text-center text-sm text-red-500">Ошибка загрузки каналов</CardContent>
          ) : (channelsQuery.data?.length ?? 0) === 0 ? (
            <CardContent className="p-6 text-center space-y-2">
              <p className="text-sm font-medium">Нет каналов</p>
              <p className="text-xs text-muted-foreground">В этом клубе пока нет каналов.</p>
            </CardContent>
          ) : (
            <CardContent className="p-4 space-y-2">
              <h2 className="text-sm font-semibold">Каналы — {selectedClub}</h2>
              {channelsQuery.data!.map((ch) => (
                <Link
                  key={ch.slug}
                  to={`/clubs/${selectedClub}/channels/${ch.slug}`}
                  className="block rounded-xl border bg-card p-3 hover:bg-accent"
                >
                  <p className="text-sm font-medium"># {ch.name}</p>
                  <p className="text-xs text-muted-foreground truncate">{ch.description || "Нет описания"}</p>
                </Link>
              ))}
              <div className="pt-4 border-t mt-4">
                <p className="text-xs text-muted-foreground">Нажми на канал, чтобы открыть чат. Realtime WebSocket уже подключен в канале.</p>
              </div>
            </CardContent>
          )}
        </Card>
      </div>

      <Card className="border-dashed">
        <CardContent className="p-4 text-center text-xs text-muted-foreground">
          Личные сообщения — скоро. Сейчас доступны каналы клубов.
        </CardContent>
      </Card>
    </div>
  );
}
