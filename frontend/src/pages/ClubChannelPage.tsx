import { useParams, Link } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { clubChannelsApi } from "@/api/clubChannels";
import { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { useAuth } from "@/stores/auth";

export function ClubChannelPage() {
  const { slug, channelSlug } = useParams();
  const { user } = useAuth();
  const qc = useQueryClient();
  const [content, setContent] = useState("");
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editContent, setEditContent] = useState("");
  const [offset, setOffset] = useState(0);

  const channelsQuery = useQuery({ queryKey: ["club-channels", slug], queryFn: () => clubChannelsApi.list(slug!) });
  const messagesQuery = useQuery({
    queryKey: ["club-messages", slug, channelSlug, offset],
    queryFn: () => clubChannelsApi.messages(slug!, channelSlug!, 50, offset),
    enabled: !!slug && !!channelSlug,
  });

  const sendMut = useMutation({
    mutationFn: () => clubChannelsApi.send(slug!, channelSlug!, content),
    onSuccess: () => {
      setContent("");
      qc.invalidateQueries({ queryKey: ["club-messages", slug, channelSlug] });
    },
  });

  const editMut = useMutation({
    mutationFn: () => clubChannelsApi.edit(slug!, channelSlug!, editingId!, editContent),
    onSuccess: () => {
      setEditingId(null);
      qc.invalidateQueries({ queryKey: ["club-messages", slug, channelSlug] });
    },
  });

  const delMut = useMutation({
    mutationFn: (id: string) => clubChannelsApi.removeMessage(slug!, channelSlug!, id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["club-messages", slug, channelSlug] }),
  });

  return (
    <div className="mx-auto max-w-6xl grid grid-cols-1 lg:grid-cols-[240px_1fr] gap-6">
      {/* Channels sidebar */}
      <div className="space-y-3">
        <Link to={`/clubs/${slug}`} className="text-sm text-muted-foreground hover:underline">← Назад в {slug}</Link>
        <h2 className="text-sm font-semibold">Каналы</h2>
        {channelsQuery.isPending && <Skeleton className="h-20 w-full" />}
        {channelsQuery.data?.map((ch) => (
          <Link key={ch.slug} to={`/clubs/${slug}/channels/${ch.slug}`} className={`block rounded-xl px-3 py-2 text-sm ${ch.slug === channelSlug ? "bg-foreground text-background" : "bg-card border hover:bg-accent"}`}>
            # {ch.name}
          </Link>
        ))}
      </div>

      {/* Messages */}
      <div className="space-y-4">
        <div className="rounded-2xl border bg-card p-4">
          <h1 className="text-lg font-semibold"># {channelSlug}</h1>
          <p className="text-xs text-muted-foreground">Сообщения канала — только участники клуба</p>
        </div>

        <Card>
          <CardContent className="p-4 space-y-3">
            {messagesQuery.isPending && <Skeleton className="h-32 w-full" />}
            {messagesQuery.isError && <p className="text-sm text-red-500">Ошибка загрузки</p>}
            {messagesQuery.data?.length === 0 && <p className="text-sm text-muted-foreground text-center py-6">Пока нет сообщений — напиши первым!</p>}
            {messagesQuery.data?.map((m) => (
              <div key={m.id} className="flex gap-3">
                <div className="h-8 w-8 rounded-full bg-foreground text-background flex items-center justify-center text-xs font-bold shrink-0">
                  {m.author?.username.slice(0, 1).toUpperCase()}
                </div>
                <div className="flex-1 rounded-xl bg-secondary/60 px-3 py-2">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-semibold">@{m.author?.username}</span>
                    <span className="text-[11px] text-muted-foreground">{new Date(m.created_at).toLocaleString("ru-RU")}</span>
                    {m.is_edited && <span className="text-[10px] text-muted-foreground">изменено</span>}
                  </div>
                  {editingId === m.id ? (
                    <div className="mt-1 flex gap-2">
                      <input value={editContent} onChange={(e) => setEditContent(e.target.value)} className="flex-1 rounded-lg border bg-background px-2 py-1 text-sm" />
                      <Button size="sm" onClick={() => editMut.mutate()} disabled={editMut.isPending}>Сохранить</Button>
                      <Button variant="ghost" size="sm" onClick={() => setEditingId(null)}>Отмена</Button>
                    </div>
                  ) : (
                    <p className="mt-1 text-sm whitespace-pre-wrap break-words">{m.content}</p>
                  )}
                  <div className="mt-1 flex gap-2 text-[11px]">
                    {m.author_id === user?.id && editingId !== m.id && (
                      <button onClick={() => { setEditingId(m.id); setEditContent(m.content); }} className="text-muted-foreground hover:underline">Изменить</button>
                    )}
                    <button onClick={() => delMut.mutate(m.id)} className="text-red-500 hover:underline">Удалить</button>
                  </div>
                </div>
              </div>
            ))}
            <div className="flex justify-center">
              <Button variant="ghost" size="sm" onClick={() => setOffset((o) => o + 50)}>Загрузить старше</Button>
            </div>
          </CardContent>
        </Card>

        <div className="rounded-2xl border bg-card p-4 space-y-2">
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="Сообщение..."
            rows={2}
            maxLength={10000}
            className="w-full rounded-xl border bg-background px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-ring"
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                if (content.trim()) sendMut.mutate();
              }
            }}
          />
          <div className="flex justify-between items-center">
            <span className="text-xs text-muted-foreground">{content.length}/10000 Shift+Enter — новая строка</span>
            <Button size="sm" onClick={() => sendMut.mutate()} disabled={sendMut.isPending || !content.trim()}>Отправить</Button>
          </div>
          {sendMut.isError && <p className="text-xs text-red-500">{(sendMut.error as Error).message}</p>}
        </div>
      </div>
    </div>
  );
}
