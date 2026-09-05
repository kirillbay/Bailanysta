import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { clubsApi } from "@/api/clubs";
import { useState } from "react";
import { Link } from "react-router-dom";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

const schema = z.object({ name: z.string().min(2).max(100), description: z.string().max(2000).optional() });
type FormValues = z.infer<typeof schema>;

export function ClubsPage() {
  const [q, setQ] = useState("");
  const [offset, setOffset] = useState(0);
  const limit = 20;
  const qc = useQueryClient();
  const [showCreate, setShowCreate] = useState(false);

  const query = useQuery({ queryKey: ["clubs", q, offset], queryFn: () => clubsApi.list(q || undefined, limit, offset) });

  const { register, handleSubmit, formState: { errors, isSubmitting }, reset } = useForm<FormValues>({ resolver: zodResolver(schema) });

  const createMut = useMutation({
    mutationFn: (values: FormValues) => clubsApi.create(values.name, values.description),
    onSuccess: (club) => {
      qc.invalidateQueries({ queryKey: ["clubs"] });
      setShowCreate(false);
      reset();
      setOffset(0);
    },
  });

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold">Клубы</h1>
        <Button size="sm" onClick={() => setShowCreate((v) => !v)}>{showCreate ? "Закрыть" : "Создать клуб"}</Button>
      </div>

      <div className="flex gap-2">
        <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Поиск по name, slug, description" className="flex-1 rounded-xl border bg-background px-3 py-2 text-sm" />
        <Button variant="outline" size="sm" onClick={() => { setOffset(0); query.refetch(); }}>Поиск</Button>
      </div>

      {showCreate && (
        <Card>
          <CardContent className="p-4 space-y-3">
            <form onSubmit={handleSubmit((v) => createMut.mutate(v))} className="space-y-3">
              <div>
                <label className="text-xs font-medium">Название</label>
                <input {...register("name")} placeholder="Python Kazakhstan" className="w-full rounded-xl border bg-background px-3 py-2 text-sm" />
                {errors.name && <p className="text-xs text-red-500">{errors.name.message}</p>}
              </div>
              <div>
                <label className="text-xs font-medium">Описание</label>
                <textarea {...register("description")} rows={3} placeholder="Сообщество Python разработчиков..." className="w-full rounded-xl border bg-background px-3 py-2 text-sm" />
                {errors.description && <p className="text-xs text-red-500">{errors.description.message}</p>}
              </div>
              {createMut.isError && <p className="text-xs text-red-500">{(createMut.error as Error).message}</p>}
              <Button type="submit" size="sm" disabled={isSubmitting || createMut.isPending}>{createMut.isPending ? "Создание..." : "Создать"}</Button>
            </form>
          </CardContent>
        </Card>
      )}

      {query.isPending && <Skeleton className="h-32 w-full rounded-2xl" />}
      {query.isError && <p className="text-sm text-red-500">Ошибка загрузки</p>}
      {query.isSuccess && query.data.length === 0 && (
        <Card><CardContent className="p-6 text-center text-sm text-muted-foreground">Клубов не найдено — создай первый!</CardContent></Card>
      )}

      <div className="grid gap-4">
        {query.data?.map((c) => (
          <Link key={c.slug} to={`/clubs/${c.slug}`} className="block rounded-2xl border bg-card p-4 hover:bg-accent">
            <div className="flex gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-foreground text-background text-sm font-bold">
                {c.name.slice(0, 2).toUpperCase()}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-semibold truncate">{c.name}</p>
                <p className="text-xs text-muted-foreground truncate">/{c.slug} · {c.members_count} участников</p>
                {c.description && <p className="mt-1 text-xs text-muted-foreground line-clamp-2">{c.description}</p>}
                {c.is_member && <span className="mt-1 inline-block rounded-full bg-secondary px-2 py-0.5 text-[11px]">{c.role}</span>}
              </div>
            </div>
          </Link>
        ))}
      </div>

      {query.data && query.data.length === limit && (
        <div className="flex justify-center">
          <Button variant="outline" onClick={() => setOffset((o) => o + limit)}>Загрузить ещё</Button>
        </div>
      )}
    </div>
  );
}
