import { Link } from "react-router-dom";
import { PostRead, postsApi } from "@/api/posts";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useState } from "react";
import { useAuth } from "@/stores/auth";
import { useMutation, useQueryClient } from "@tanstack/react-query";

function formatDate(s: string) {
  try {
    return new Date(s).toLocaleString("ru-RU");
  } catch {
    return s;
  }
}

export function PostCard({ post, onUpdated }: { post: PostRead; onUpdated?: () => void }) {
  const { user } = useAuth();
  const qc = useQueryClient();
  const isOwner = user?.id === post.author_id;
  const [editing, setEditing] = useState(false);
  const [editContent, setEditContent] = useState(post.content);
  const [confirmDelete, setConfirmDelete] = useState(false);

  const updateMut = useMutation({
    mutationFn: () => postsApi.update(post.id, editContent),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["posts"] });
      qc.invalidateQueries({ queryKey: ["user-posts"] });
      setEditing(false);
      onUpdated?.();
    },
  });

  const deleteMut = useMutation({
    mutationFn: () => postsApi.remove(post.id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["posts"] });
      qc.invalidateQueries({ queryKey: ["user-posts"] });
      onUpdated?.();
    },
  });

  return (
    <Card className="overflow-hidden">
      <CardContent className="p-4 space-y-3">
        <div className="flex gap-3">
          <Link to={`/profile/${post.author.username}`}>
            {post.author.avatar_url ? (
              <img src={postsApi.resolveUrl(post.author.avatar_url)} alt={post.author.username} className="h-9 w-9 rounded-full object-cover" />
            ) : (
              <div className="flex h-9 w-9 items-center justify-center rounded-full bg-foreground text-background text-sm font-bold">
                {post.author.username.slice(0, 1).toUpperCase()}
              </div>
            )}
          </Link>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <Link to={`/profile/${post.author.username}`} className="text-sm font-semibold hover:underline">
                {post.author.display_name || post.author.username}
              </Link>
              <span className="text-xs text-muted-foreground">@{post.author.username}</span>
              <span className="text-xs text-muted-foreground">· {formatDate(post.created_at)}</span>
            </div>

            {editing ? (
              <div className="mt-2 space-y-2">
                <textarea value={editContent} onChange={(e) => setEditContent(e.target.value)} rows={3} className="w-full rounded-xl border bg-background px-3 py-2 text-sm" />
                <div className="flex gap-2">
                  <Button size="sm" onClick={() => updateMut.mutate()} disabled={updateMut.isPending}>
                    Сохранить
                  </Button>
                  <Button variant="outline" size="sm" onClick={() => setEditing(false)}>
                    Отмена
                  </Button>
                </div>
                {updateMut.isError && <p className="text-xs text-red-500">{(updateMut.error as Error).message}</p>}
              </div>
            ) : (
              <p className="mt-1 whitespace-pre-wrap break-words text-sm leading-relaxed">
                {post.content.split(/(#\w+)/g).map((part, i) =>
                  part.startsWith("#") ? (
                    <span key={i} className="text-primary font-medium">
                      {part}
                    </span>
                  ) : (
                    <span key={i}>{part}</span>
                  )
                )}
              </p>
            )}

            {post.media.length > 0 && !editing && (
              <div className={`mt-3 grid gap-2 ${post.media.length === 1 ? "grid-cols-1" : "grid-cols-2"}`}>
                {post.media.map((m) => (
                  <img key={m.id} src={postsApi.resolveUrl(m.url)} alt="post media" className="rounded-xl border object-cover max-h-80 w-full" />
                ))}
              </div>
            )}

            {post.hashtags.length > 0 && !editing && (
              <div className="mt-2 flex flex-wrap gap-1">
                {post.hashtags.map((h) => (
                  <span key={h} className="rounded-full bg-secondary px-2 py-0.5 text-xs">#{h}</span>
                ))}
              </div>
            )}

            <div className="mt-3 flex gap-2">
              <Link to={`/posts/${post.id}`} className="text-xs text-muted-foreground hover:underline">
                Открыть
              </Link>
              {isOwner && !editing && (
                <>
                  <button onClick={() => setEditing(true)} className="text-xs text-muted-foreground hover:underline">
                    Редактировать
                  </button>
                  {!confirmDelete ? (
                    <button onClick={() => setConfirmDelete(true)} className="text-xs text-red-500 hover:underline">
                      Удалить
                    </button>
                  ) : (
                    <span className="flex gap-1 text-xs">
                      <button onClick={() => deleteMut.mutate()} className="text-red-600 font-medium">
                        Подтвердить
                      </button>
                      <button onClick={() => setConfirmDelete(false)} className="text-muted-foreground">
                        Отмена
                      </button>
                    </span>
                  )}
                </>
              )}
            </div>
            {deleteMut.isError && <p className="text-xs text-red-500">{(deleteMut.error as Error).message}</p>}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
