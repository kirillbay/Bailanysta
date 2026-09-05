import { useParams, Link } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { clubsApi } from "@/api/clubs";
import { clubChannelsApi } from "@/api/clubChannels";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { useState } from "react";
import { useAuth } from "@/stores/auth";

function ChannelsSection({ slug, isAdmin }: { slug: string; isAdmin: boolean }) {
  const qc = useQueryClient();
  const query = useQuery({ queryKey: ["channels", slug], queryFn: () => clubChannelsApi.list(slug) });
  const [name, setName] = useState("");
  const [desc, setDesc] = useState("");
  const [editing, setEditing] = useState<string | null>(null);

  const createMut = useMutation({
    mutationFn: () => clubChannelsApi.create(slug, name, desc || undefined),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["channels", slug] });
      setName("");
      setDesc("");
    },
  });

  return (
    <div className="rounded-2xl border bg-card p-4 space-y-3">
      <h2 className="text-sm font-semibold">Channels</h2>
      {query.isPending && <Skeleton className="h-20 w-full" />}
      {query.data?.map((ch) => (
        <div key={ch.slug} className="flex items-center gap-3 rounded-xl bg-secondary p-3">
          <Link to={`/clubs/${slug}/channels/${ch.slug}`} className="flex-1">
            <p className="text-sm font-medium"># {ch.name}</p>
            {ch.description && <p className="text-xs text-muted-foreground">{ch.description}</p>}
          </Link>
          {isAdmin && (
            <div className="flex gap-1">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => {
                  const newName = prompt("New name", ch.name);
                  if (newName) clubChannelsApi.update(slug, ch.slug, { name: newName }).then(() => qc.invalidateQueries({ queryKey: ["channels", slug] }));
                }}
              >
                Edit
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => {
                  if (confirm("Delete channel?")) clubChannelsApi.remove(slug, ch.slug).then(() => qc.invalidateQueries({ queryKey: ["channels", slug] }));
                }}
              >
                Delete
              </Button>
            </div>
          )}
        </div>
      ))}
      {isAdmin && (
        <div className="space-y-2 border-t pt-3">
          <p className="text-xs font-medium">Создать канал (owner/admin)</p>
          <input value={name} onChange={(e) => setName(e.target.value)} placeholder="general" className="w-full rounded-xl border px-3 py-1.5 text-sm" />
          <input value={desc} onChange={(e) => setDesc(e.target.value)} placeholder="Описание (необязательно)" className="w-full rounded-xl border px-3 py-1.5 text-sm" />
          <Button size="sm" onClick={() => createMut.mutate()} disabled={createMut.isPending || !name.trim()}>
            Создать
          </Button>
          {createMut.isError && <p className="text-xs text-red-500">{(createMut.error as Error).message}</p>}
        </div>
      )}
      {!isAdmin && query.data?.length === 0 && <p className="text-xs text-muted-foreground">Пока нет каналов</p>}
    </div>
  );
}

export function ClubPage() {
  const { slug } = useParams();
  const { user: me } = useAuth();
  const qc = useQueryClient();
  const [msg, setMsg] = useState<string | null>(null);
  const [editOpen, setEditOpen] = useState(false);
  const [editName, setEditName] = useState("");
  const [editDesc, setEditDesc] = useState("");

  const clubQuery = useQuery({ queryKey: ["club", slug], queryFn: () => clubsApi.get(slug!), enabled: !!slug });
  const membersQuery = useQuery({ queryKey: ["club-members", slug], queryFn: () => clubsApi.members(slug!, 50, 0), enabled: !!slug });

  const joinMut = useMutation({
    mutationFn: () => clubsApi.join(slug!),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["club", slug] }); qc.invalidateQueries({ queryKey: ["club-members", slug] }); setMsg("Вступил"); },
    onError: (e: any) => setMsg(e.message),
  });
  const leaveMut = useMutation({
    mutationFn: () => clubsApi.leave(slug!),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["club", slug] }); qc.invalidateQueries({ queryKey: ["club-members", slug] }); setMsg("Вышел"); },
    onError: (e: any) => setMsg(e.message),
  });
  const deleteMut = useMutation({
    mutationFn: () => clubsApi.remove(slug!),
    onSuccess: () => { window.location.href = "/clubs"; },
    onError: (e: any) => setMsg(e.message),
  });
  const updateMut = useMutation({
    mutationFn: () => clubsApi.update(slug!, { name: editName || undefined, description: editDesc || undefined }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["club", slug] }); setEditOpen(false); setMsg("Обновлено"); },
    onError: (e: any) => setMsg(e.message),
  });

  if (clubQuery.isPending) return <div className="mx-auto max-w-3xl"><Skeleton className="h-40 w-full rounded-2xl" /></div>;
  if (clubQuery.isError) return <div className="mx-auto max-w-3xl text-center py-12"><p className="text-sm">Клуб не найден</p><Link to="/clubs" className="text-xs underline">Назад</Link></div>;

  const club: any = clubQuery.data;
  const isOwner = club.role === "owner";
  const isAdmin = club.role === "admin" || isOwner;
  const isMember = club.is_member;

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div className="overflow-hidden rounded-[24px] border bg-card">
        <div className="h-32 bg-gradient-to-br from-violet-500 via-indigo-500 to-sky-500 relative">
          {club.cover_url && <img src={club.cover_url} alt="cover" className="h-full w-full object-cover" />}
        </div>
        <div className="p-5">
          <div className="flex gap-4">
            <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-foreground text-background text-lg font-bold -mt-8 border-4 border-card">
              {club.name.slice(0, 2).toUpperCase()}
            </div>
            <div className="flex-1">
              <h1 className="text-lg font-semibold">{club.name}</h1>
              <p className="text-sm text-muted-foreground">/{club.slug} · {club.members_count} участников · owner {club.owner_id.slice(0, 8)}</p>
              {club.description && <p className="mt-2 text-sm whitespace-pre-wrap">{club.description}</p>}
              {club.role && <span className="mt-2 inline-block rounded-full bg-secondary px-2 py-0.5 text-xs">{club.role}</span>}
            </div>
          </div>

          <div className="mt-4 flex flex-wrap gap-2">
            {!isMember ? (
              <Button size="sm" onClick={() => joinMut.mutate()} disabled={joinMut.isPending}>Вступить</Button>
            ) : !isOwner ? (
              <Button variant="outline" size="sm" onClick={() => leaveMut.mutate()} disabled={leaveMut.isPending}>Выйти</Button>
            ) : (
              <span className="text-xs text-muted-foreground">Ты владелец</span>
            )}
            {(isOwner || isAdmin) && <Button variant="outline" size="sm" onClick={() => { setEditName(club.name); setEditDesc(club.description || ""); setEditOpen((v) => !v); }}>{editOpen ? "Закрыть" : "Редактировать"}</Button>}
            {isOwner && <Button variant="ghost" size="sm" onClick={() => { if (confirm("Удалить клуб?")) deleteMut.mutate(); }}>Удалить</Button>}
            <label className="inline-flex cursor-pointer items-center rounded-xl border px-3 py-1.5 text-xs hover:bg-accent">
              Аватар
              <input type="file" accept="image/jpeg,image/png,image/webp" className="hidden" onChange={(e) => e.target.files?.[0] && clubsApi.uploadAvatar(slug!, e.target.files[0]).then(() => clubQuery.refetch())} />
            </label>
            <label className="inline-flex cursor-pointer items-center rounded-xl border px-3 py-1.5 text-xs hover:bg-accent">
              Обложка
              <input type="file" accept="image/jpeg,image/png,image/webp" className="hidden" onChange={(e) => e.target.files?.[0] && clubsApi.uploadCover(slug!, e.target.files[0]).then(() => clubQuery.refetch())} />
            </label>
          </div>
          {msg && <p className="mt-2 text-xs bg-secondary p-2 rounded-xl">{msg}</p>}

          {editOpen && (
            <Card className="mt-4">
              <CardContent className="p-4 space-y-2">
                <input value={editName} onChange={(e) => setEditName(e.target.value)} placeholder="Название" className="w-full rounded-xl border px-3 py-2 text-sm" />
                <textarea value={editDesc} onChange={(e) => setEditDesc(e.target.value)} placeholder="Описание" rows={3} className="w-full rounded-xl border px-3 py-2 text-sm" />
                <Button size="sm" onClick={() => updateMut.mutate()} disabled={updateMut.isPending}>Сохранить</Button>
              </CardContent>
            </Card>
          )}
        </div>
      </div>

      <ChannelsSection slug={club.slug} isAdmin={isAdmin} />

      <Card>
        <CardContent className="p-4 space-y-3">
          <h2 className="text-sm font-semibold">Участники ({membersQuery.data?.total ?? club.members_count})</h2>
          {membersQuery.isPending && <Skeleton className="h-20 w-full" />}
          {membersQuery.data?.items.map((m: any) => (
            <div key={m.id} className="flex items-center gap-3 rounded-xl border p-3">
              <div className="h-8 w-8 rounded-full bg-foreground text-background flex items-center justify-center text-xs font-bold">{m.username.slice(0, 1).toUpperCase()}</div>
              <div className="flex-1">
                <p className="text-sm font-medium">@{m.username} · {m.role}</p>
                <p className="text-xs text-muted-foreground">{m.display_name || ""}</p>
              </div>
              {me && m.username !== me.username && (isOwner || (isAdmin && m.role === "member") || (m.role === "member" && club.role === "moderator")) && (
                <div className="flex gap-1">
                  {isOwner && m.role !== "owner" && (
                    <select value={m.role} onChange={(e) => clubsApi.updateRole(slug!, m.username, e.target.value).then(() => membersQuery.refetch()).catch((err) => setMsg(err.message))} className="rounded-lg border px-2 py-1 text-xs">
                      <option value="member">member</option>
                      <option value="moderator">moderator</option>
                      <option value="admin">admin</option>
                    </select>
                  )}
                  <Button variant="ghost" size="sm" onClick={() => clubsApi.removeMember(slug!, m.username).then(() => membersQuery.refetch()).catch((e) => setMsg(e.message))}>Удалить</Button>
                </div>
              )}
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}
