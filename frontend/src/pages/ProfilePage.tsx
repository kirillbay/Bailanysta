import { useParams, Link } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { usersApi } from "@/api/users";
import { followsApi } from "@/api/follows";
import { projectsApi } from "@/api/projects";
import { ProjectCard } from "@/components/ProjectCard";
import { ProjectForm, ProjectFormValues } from "@/components/ProjectForm";
import { useAuth } from "@/stores/auth";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

const editSchema = z.object({
  display_name: z.string().max(100).optional().or(z.literal("")),
  bio: z.string().max(500).optional().or(z.literal("")),
});
type EditValues = z.infer<typeof editSchema>;

function Avatar({ url, username }: { url: string | null; username: string }) {
  const src = usersApi.resolveUrl(url);
  if (!src) {
    return (
      <div className="flex h-24 w-24 items-center justify-center rounded-2xl bg-foreground text-background text-2xl font-bold border-4 border-card shadow-sm">
        {username.slice(0, 1).toUpperCase()}
      </div>
    );
  }
  return <img src={src} alt={username} className="h-24 w-24 rounded-2xl object-cover border-4 border-card shadow-sm bg-card" />;
}

export function ProfilePage() {
  const { username } = useParams();
  const { user: me } = useAuth();
  const qc = useQueryClient();
  const isOwn = !username || (me && me.username === username);
  const targetUsername = username ?? me?.username ?? "";

  const publicQuery = useQuery({
    queryKey: ["profile", targetUsername],
    queryFn: () => usersApi.public(targetUsername),
    enabled: !!targetUsername && !isOwn,
  });

  const meQuery = useQuery({
    queryKey: ["profile-me", me?.username],
    queryFn: () => usersApi.me(),
    enabled: !!isOwn && !!me,
  });

  const data: any = isOwn ? (meQuery.data as any) ?? me : publicQuery.data;
  const isLoading = isOwn ? meQuery.isPending && !me : publicQuery.isPending;
  const isError = isOwn ? meQuery.isError : publicQuery.isError;

  const [editOpen, setEditOpen] = useState(false);
  const [avatarPreview, setAvatarPreview] = useState<string | null>(null);
  const [coverPreview, setCoverPreview] = useState<string | null>(null);
  const [uploading, setUploading] = useState<"avatar" | "cover" | null>(null);
  const [msg, setMsg] = useState<string | null>(null);
  const [followOptimistic, setFollowOptimistic] = useState<boolean | null>(null);
  const [followersCountOptimistic, setFollowersCountOptimistic] = useState<number | null>(null);

  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<EditValues>({
    resolver: zodResolver(editSchema),
    defaultValues: { display_name: data?.display_name ?? "", bio: data?.bio ?? "" },
  });

  const mutation = useMutation({
    mutationFn: (values: EditValues) => usersApi.update({ display_name: values.display_name || null, bio: values.bio || null }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["profile"] });
      qc.invalidateQueries({ queryKey: ["profile-me"] });
      qc.invalidateQueries({ queryKey: ["auth", "me"] });
      setMsg("Профиль обновлён");
      setEditOpen(false);
      setTimeout(() => setMsg(null), 3000);
    },
    onError: (e: any) => setMsg(e.message || "Ошибка"),
  });

  const followMut = useMutation({
    mutationFn: () => {
      const currently = followOptimistic ?? data?.is_following ?? false;
      return currently ? followsApi.unfollow(targetUsername) : followsApi.follow(targetUsername);
    },
    onMutate: () => {
      const currently = followOptimistic ?? data?.is_following ?? false;
      const currentCount = followersCountOptimistic ?? data?.followers_count ?? 0;
      setFollowOptimistic(!currently);
      setFollowersCountOptimistic(currently ? currentCount - 1 : currentCount + 1);
      // Optimistically update cache for instant feedback
      qc.setQueryData(["profile", targetUsername], (old: any) => {
        if (!old) return old;
        return { ...old, is_following: !currently, followers_count: currently ? (old.followers_count ?? 1) - 1 : (old.followers_count ?? 0) + 1 };
      });
    },
    onError: () => {
      setFollowOptimistic(null);
      setFollowersCountOptimistic(null);
      qc.invalidateQueries({ queryKey: ["profile", targetUsername] });
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["profile", targetUsername] });
      // Clear optimistic after server confirms — let refetched data take over
      setTimeout(() => {
        setFollowOptimistic(null);
        setFollowersCountOptimistic(null);
      }, 500);
    },
  });

  const handleFile = async (file: File, type: "avatar" | "cover") => {
    setUploading(type);
    setMsg(null);
    try {
      const url = URL.createObjectURL(file);
      if (type === "avatar") setAvatarPreview(url);
      else setCoverPreview(url);
      if (type === "avatar") await usersApi.uploadAvatar(file);
      else await usersApi.uploadCover(file);
      qc.invalidateQueries({ queryKey: ["profile"] });
      qc.invalidateQueries({ queryKey: ["profile-me"] });
      qc.invalidateQueries({ queryKey: ["auth", "me"] });
      setMsg(type === "avatar" ? "Аватар обновлён" : "Обложка обновлена");
      setTimeout(() => setMsg(null), 3000);
      setTimeout(() => {
        if (type === "avatar") setAvatarPreview(null);
        else setCoverPreview(null);
      }, 1000);
    } catch (e: any) {
      setMsg(e.message || "Ошибка загрузки");
      if (type === "avatar") setAvatarPreview(null);
      else setCoverPreview(null);
    } finally {
      setUploading(null);
    }
  };

  if (!targetUsername) return <div className="text-center text-sm text-muted-foreground">Загрузка профиля...</div>;
  if (isLoading) {
    return (
      <div className="mx-auto max-w-2xl space-y-4">
        <Skeleton className="h-32 w-full rounded-2xl" />
        <Skeleton className="h-24 w-full rounded-2xl" />
      </div>
    );
  }
  if (isError || !data) {
    return (
      <div className="mx-auto max-w-2xl text-center space-y-3 py-12">
        <p className="text-sm font-medium">Профиль не найден</p>
        <p className="text-xs text-muted-foreground">Пользователь @{targetUsername} не существует.</p>
        <Link to="/" className="inline-block rounded-xl bg-foreground px-4 py-2 text-sm text-background">На главную</Link>
      </div>
    );
  }

  const coverUrl = usersApi.resolveUrl((data as any).cover_url);
  const isFollowing = followOptimistic ?? (data as any).is_following ?? false;
  const followersCount = followersCountOptimistic ?? (data as any).followers_count ?? 0;
  const followingCount = (data as any).following_count ?? 0;

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div className="rounded-[24px] border bg-card">
        <div className="h-44 w-full bg-gradient-to-br from-violet-500 via-indigo-500 to-sky-500 relative rounded-t-[24px] overflow-hidden">
          {coverUrl && <img src={coverUrl} alt="cover" className="h-full w-full object-cover" />}
          {coverPreview && <img src={coverPreview} alt="preview" className="h-full w-full object-cover opacity-60" />}
        </div>
        <div className="p-5">
          <div className="flex gap-4">
            <div className="-mt-16 relative z-10">
              {avatarPreview ? (
                <img src={avatarPreview} alt="preview" className="h-24 w-24 rounded-2xl object-cover border-4 border-card shadow-sm bg-card" />
              ) : (
                <Avatar url={(data as any).avatar_url} username={data.username} />
              )}
            </div>
            <div className="flex-1 min-w-0 pt-1">
              <h1 className="text-lg font-semibold truncate">{(data as any).display_name || data.username}</h1>
              <p className="text-sm text-muted-foreground">@{data.username}</p>
              {(data as any).bio && <p className="mt-2 text-sm leading-relaxed whitespace-pre-wrap">{(data as any).bio}</p>}
              <div className="mt-2 flex gap-4 text-xs text-muted-foreground">
                <span><b className="text-foreground">{followersCount}</b> followers</span>
                <span><b className="text-foreground">{followingCount}</b> following</span>
              </div>
              <p className="mt-1 text-xs text-muted-foreground">С нами с {new Date(data.created_at).toLocaleDateString("ru-RU")}</p>
            </div>
          </div>

          {isOwn ? (
            <div className="mt-4 flex flex-wrap gap-2">
              <Button variant="outline" size="sm" onClick={() => setEditOpen((v) => !v)}>
                {editOpen ? "Закрыть" : "Редактировать профиль"}
              </Button>
              <label className="inline-flex cursor-pointer items-center rounded-xl border px-3 py-1.5 text-xs font-medium hover:bg-accent">
                {uploading === "avatar" ? "Загрузка..." : "Загрузить аватар"}
                <input type="file" accept="image/jpeg,image/png,image/webp" className="hidden" onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0], "avatar")} disabled={!!uploading} />
              </label>
              <label className="inline-flex cursor-pointer items-center rounded-xl border px-3 py-1.5 text-xs font-medium hover:bg-accent">
                {uploading === "cover" ? "Загрузка..." : "Загрузить обложку"}
                <input type="file" accept="image/jpeg,image/png,image/webp" className="hidden" onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0], "cover")} disabled={!!uploading} />
              </label>
            </div>
          ) : (
            <div className="mt-4">
              <Button size="sm" variant={isFollowing ? "outline" : "default"} onClick={() => followMut.mutate()} disabled={followMut.isPending}>
                {isFollowing ? "Отписаться" : "Подписаться"}
              </Button>
              <Link to={`/profile/${data.username}/followers`} className="ml-3 text-xs text-muted-foreground hover:underline">Followers</Link>
              <Link to={`/profile/${data.username}/following`} className="ml-2 text-xs text-muted-foreground hover:underline">Following</Link>
            </div>
          )}

          {msg && <p className="mt-3 rounded-xl bg-secondary p-2 text-xs">{msg}</p>}

          {isOwn && editOpen && (
            <Card className="mt-4">
              <CardContent className="p-4 space-y-3">
                <form onSubmit={handleSubmit((v) => mutation.mutate(v))} className="space-y-3">
                  <div className="space-y-1">
                    <label className="text-xs font-medium">Display name</label>
                    <input {...register("display_name")} placeholder="Кирилл" className="w-full rounded-xl border bg-background px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-ring" />
                    {errors.display_name && <p className="text-xs text-red-500">{errors.display_name.message}</p>}
                  </div>
                  <div className="space-y-1">
                    <label className="text-xs font-medium">Bio (до 500)</label>
                    <textarea {...register("bio")} rows={3} placeholder="Расскажи о себе..." className="w-full rounded-xl border bg-background px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-ring" />
                    {errors.bio && <p className="text-xs text-red-500">{errors.bio.message}</p>}
                  </div>
                  <Button type="submit" size="sm" disabled={isSubmitting || mutation.isPending}>
                    {mutation.isPending ? "Сохранение..." : "Сохранить"}
                  </Button>
                </form>
              </CardContent>
            </Card>
          )}
        </div>
      </div>

      <ProfileProjectsSection username={data.username} isOwn={!!isOwn} />
    </div>
  );
}

function ProfileProjectsSection({ username, isOwn }: { username: string; isOwn: boolean }) {
  const qc = useQueryClient();
  const [tab, setTab] = useState<"posts" | "projects">("projects");
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState<any | null>(null);
  const [imgUploading, setImgUploading] = useState<string | null>(null);

  const projectsQuery = useQuery({
    queryKey: ["projects-user", username],
    queryFn: () => projectsApi.listUser(username, { limit: 50 }),
    enabled: !!username,
  });

  const createMut = useMutation({
    mutationFn: (vals: ProjectFormValues) => projectsApi.create({ name: vals.name, description: vals.description, technologies: vals.technologies, github_url: vals.github_url || null, demo_url: vals.demo_url || null, status: vals.status }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["projects-user", username] }); setShowForm(false); },
  });
  const updateMut = useMutation({
    mutationFn: (vals: ProjectFormValues) => projectsApi.update(editing.id, { name: vals.name, description: vals.description, technologies: vals.technologies, github_url: vals.github_url || null, demo_url: vals.demo_url || null, status: vals.status }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["projects-user", username] }); setEditing(null); },
  });
  const deleteMut = useMutation({
    mutationFn: (id: string) => projectsApi.delete(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["projects-user", username] }),
  });

  const handleImage = async (id: string, file: File) => {
    setImgUploading(id);
    try {
      await projectsApi.uploadImage(id, file);
      qc.invalidateQueries({ queryKey: ["projects-user", username] });
    } finally { setImgUploading(null); }
  };

  return (
    <div className="space-y-4">
      <div className="flex gap-2 border-b">
        <button onClick={() => setTab("posts")} className={`px-3 py-2 text-sm font-medium border-b-2 ${tab === "posts" ? "border-foreground" : "border-transparent text-muted-foreground"}`}>Posts</button>
        <button onClick={() => setTab("projects")} className={`px-3 py-2 text-sm font-medium border-b-2 ${tab === "projects" ? "border-foreground" : "border-transparent text-muted-foreground"}`}>Projects</button>
      </div>

      {tab === "posts" && (
        <Card><CardContent className="p-6 text-center"><p className="text-sm font-medium">Посты</p><p className="text-xs text-muted-foreground">Посты пользователя — через feed и /profile/:username/posts (STEP5).</p></CardContent></Card>
      )}

      {tab === "projects" && (
        <div className="space-y-4">
          {isOwn && (
            <div className="flex justify-between items-center">
              <h3 className="text-sm font-semibold">Projects</h3>
              <Button size="sm" variant="outline" onClick={() => { setEditing(null); setShowForm((v) => !v); }}>{showForm ? "Close" : "Add project"}</Button>
            </div>
          )}
          {isOwn && showForm && <ProjectForm onSubmit={(v) => createMut.mutate(v)} onCancel={() => setShowForm(false)} isSubmitting={createMut.isPending} />}
          {isOwn && editing && <ProjectForm defaultValues={{ ...editing, github_url: editing.github_url ?? "", demo_url: editing.demo_url ?? "" }} onSubmit={(v) => updateMut.mutate(v)} onCancel={() => setEditing(null)} isSubmitting={updateMut.isPending} />}

          {projectsQuery.isPending ? (
            <div className="grid gap-4 md:grid-cols-2"><Skeleton className="h-64 rounded-[20px]" /><Skeleton className="h-64 rounded-[20px]" /></div>
          ) : (projectsQuery.data?.length ?? 0) === 0 ? (
            <Card><CardContent className="p-6 text-center"><p className="text-sm font-medium">No projects yet</p><p className="text-xs text-muted-foreground mt-1">{isOwn ? "Add your first project" : "This developer hasn't added any projects yet."}</p></CardContent></Card>
          ) : (
            <div className="grid gap-4 md:grid-cols-2">
              {(projectsQuery.data ?? []).map((p) => (
                <div key={p.id} className="space-y-2">
                  <ProjectCard project={p} isOwner={isOwn} onEdit={() => { setShowForm(false); setEditing(p); }} onDelete={() => { if (confirm("Delete project?")) deleteMut.mutate(p.id); }} />
                  {isOwn && (
                    <label className="inline-flex cursor-pointer items-center rounded-xl border px-3 py-1.5 text-xs font-medium hover:bg-accent">
                      {imgUploading === p.id ? "Uploading..." : "Upload image"}
                      <input type="file" accept="image/jpeg,image/png,image/webp" className="hidden" onChange={(e) => e.target.files?.[0] && handleImage(p.id, e.target.files[0])} disabled={!!imgUploading} />
                    </label>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
