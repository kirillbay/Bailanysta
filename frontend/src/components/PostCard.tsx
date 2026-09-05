import { Link } from "react-router-dom";
import { PostRead, postsApi } from "@/api/posts";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useState } from "react";
import { useAuth } from "@/stores/auth";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Heart, MessageCircle, Repeat2, Bookmark, Share2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { commentsApi } from "@/api/comments";
import { useQuery } from "@tanstack/react-query";

function formatDate(s: string) {
  try {
    return new Date(s).toLocaleString("ru-RU");
  } catch {
    return s;
  }
}

function CommentSection({ postId, onCountChange }: { postId: string; onCountChange?: () => void }) {
  const [content, setContent] = useState("");
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editContent, setEditContent] = useState("");
  const { user } = useAuth();
  const qc = useQueryClient();

  const query = useQuery({
    queryKey: ["comments", postId],
    queryFn: () => commentsApi.list(postId, 20, 0),
  });

  const createMut = useMutation({
    mutationFn: () => commentsApi.create(postId, content),
    onSuccess: () => {
      setContent("");
      qc.invalidateQueries({ queryKey: ["comments", postId] });
      qc.invalidateQueries({ queryKey: ["feed"] });
      qc.invalidateQueries({ queryKey: ["post"] });
      onCountChange?.();
    },
  });

  const updateMut = useMutation({
    mutationFn: () => commentsApi.update(editingId!, editContent),
    onSuccess: () => {
      setEditingId(null);
      qc.invalidateQueries({ queryKey: ["comments", postId] });
    },
  });

  const deleteMut = useMutation({
    mutationFn: (id: string) => commentsApi.remove(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["comments", postId] });
      qc.invalidateQueries({ queryKey: ["feed"] });
      onCountChange?.();
    },
  });

  return (
    <div className="border-t pt-3 space-y-3">
      <div className="flex gap-2">
        <input
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="Написать комментарий..."
          maxLength={2000}
          className="flex-1 rounded-xl border bg-background px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-ring"
        />
        <Button size="sm" onClick={() => createMut.mutate()} disabled={createMut.isPending || !content.trim()}>
          Отправить
        </Button>
      </div>
      {createMut.isError && <p className="text-xs text-red-500">{(createMut.error as Error).message}</p>}
      {query.isPending && <p className="text-xs text-muted-foreground">Загрузка комментариев...</p>}
      {query.isError && <p className="text-xs text-red-500">Ошибка загрузки комментариев</p>}
      {query.data?.length === 0 && <p className="text-xs text-muted-foreground">Пока нет комментариев</p>}
      {query.data?.map((c) => (
        <div key={c.id} className="flex gap-2">
          <div className="flex h-7 w-7 items-center justify-center rounded-full bg-secondary text-xs font-bold shrink-0">
            {c.author?.username.slice(0, 1).toUpperCase() ?? "?"}
          </div>
          <div className="flex-1 rounded-xl bg-secondary/60 px-3 py-2">
            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold">@{c.author?.username}</span>
              <span className="text-[11px] text-muted-foreground">{formatDate(c.created_at)}</span>
            </div>
            {editingId === c.id ? (
              <div className="mt-1 flex gap-2">
                <input value={editContent} onChange={(e) => setEditContent(e.target.value)} className="flex-1 rounded-lg border bg-background px-2 py-1 text-sm" />
                <Button size="sm" onClick={() => updateMut.mutate()} disabled={updateMut.isPending}>
                  Сохранить
                </Button>
                <Button variant="ghost" size="sm" onClick={() => setEditingId(null)}>
                  Отмена
                </Button>
              </div>
            ) : (
              <p className="mt-1 text-sm whitespace-pre-wrap break-words">{c.content}</p>
            )}
            {c.author_id === user?.id && editingId !== c.id && (
              <div className="mt-1 flex gap-2 text-[11px]">
                <button onClick={() => { setEditingId(c.id); setEditContent(c.content); }} className="text-muted-foreground hover:underline">
                  Изменить
                </button>
                <button onClick={() => deleteMut.mutate(c.id)} className="text-red-500 hover:underline">
                  Удалить
                </button>
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}

export function PostCard({ post, onUpdated, withComments = false }: { post: PostRead; onUpdated?: () => void; withComments?: boolean }) {
  const { user } = useAuth();
  const qc = useQueryClient();
  const isOwner = user?.id === post.author_id;
  const [editing, setEditing] = useState(false);
  const [editContent, setEditContent] = useState(post.content);
  const [confirmDelete, setConfirmDelete] = useState(false);
  const [showComments, setShowComments] = useState(withComments);
  const [optimistic, setOptimistic] = useState(post);

  // sync optimistic when post changes
  // useEffect not needed for simplicity, rely on prop

  const updateMut = useMutation({
    mutationFn: () => postsApi.update(post.id, editContent),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["feed"] });
      qc.invalidateQueries({ queryKey: ["user-posts"] });
      qc.invalidateQueries({ queryKey: ["post", post.id] });
      setEditing(false);
      onUpdated?.();
    },
  });

  const deleteMut = useMutation({
    mutationFn: () => postsApi.remove(post.id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["feed"] });
      qc.invalidateQueries({ queryKey: ["user-posts"] });
      qc.invalidateQueries({ queryKey: ["bookmarks"] });
      onUpdated?.();
    },
  });

  const toggleLike = () => {
    const wasLiked = optimistic.liked_by_me;
    const newLiked = !wasLiked;
    setOptimistic((prev) => ({
      ...prev,
      liked_by_me: newLiked,
      likes_count: prev.likes_count + (newLiked ? 1 : -1),
    }));
    const promise = wasLiked ? postsApi.unlike(post.id) : postsApi.like(post.id);
    promise.catch(() => {
      // rollback
      setOptimistic((prev) => ({
        ...prev,
        liked_by_me: wasLiked,
        likes_count: prev.likes_count + (wasLiked ? 1 : -1),
      }));
    }).then(() => {
      qc.invalidateQueries({ queryKey: ["feed"] });
    });
  };

  const toggleRepost = () => {
    const was = optimistic.reposted_by_me;
    setOptimistic((prev) => ({
      ...prev,
      reposted_by_me: !was,
      reposts_count: prev.reposts_count + (was ? -1 : 1),
    }));
    const p = was ? postsApi.unrepost(post.id) : postsApi.repost(post.id);
    p.catch(() => {
      setOptimistic((prev) => ({
        ...prev,
        reposted_by_me: was,
        reposts_count: prev.reposts_count + (was ? 1 : -1),
      }));
    }).then(() => qc.invalidateQueries({ queryKey: ["feed"] }));
  };

  const toggleBookmark = () => {
    const was = optimistic.bookmarked_by_me;
    setOptimistic((prev) => ({ ...prev, bookmarked_by_me: !was }));
    const p = was ? postsApi.unbookmark(post.id) : postsApi.bookmark(post.id);
    p.catch(() => {
      setOptimistic((prev) => ({ ...prev, bookmarked_by_me: was }));
    }).then(() => {
      qc.invalidateQueries({ queryKey: ["bookmarks"] });
    });
  };

  const current = optimistic;

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
                    <Link key={i} to={`/hashtags/${part.slice(1)}`} className="text-primary font-medium hover:underline">
                      {part}
                    </Link>
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
                  <Link key={h} to={`/hashtags/${h}`} className="rounded-full bg-secondary px-2 py-0.5 text-xs hover:bg-accent">#{h}</Link>
                ))}
              </div>
            )}

            {/* Interaction bar */}
            <div className="mt-3 flex items-center gap-1 text-xs">
              <button onClick={toggleLike} className={cn("flex items-center gap-1 rounded-full px-2.5 py-1 hover:bg-accent", current.liked_by_me && "text-red-500")}>
                <Heart className={cn("h-4 w-4", current.liked_by_me && "fill-red-500 text-red-500")} />
                {current.likes_count}
              </button>
              <button onClick={() => setShowComments((v) => !v)} className="flex items-center gap-1 rounded-full px-2.5 py-1 hover:bg-accent">
                <MessageCircle className="h-4 w-4" />
                {current.comments_count}
              </button>
              <button onClick={toggleRepost} className={cn("flex items-center gap-1 rounded-full px-2.5 py-1 hover:bg-accent", current.reposted_by_me && "text-green-600")}>
                <Repeat2 className="h-4 w-4" />
                {current.reposts_count}
              </button>
              <button onClick={toggleBookmark} className={cn("flex items-center gap-1 rounded-full px-2.5 py-1 hover:bg-accent", current.bookmarked_by_me && "text-blue-600")}>
                <Bookmark className={cn("h-4 w-4", current.bookmarked_by_me && "fill-blue-600")} />
              </button>
              <button
                onClick={() => {
                  const url = `${window.location.origin}/posts/${post.id}`;
                  navigator.clipboard.writeText(url);
                }}
                className="flex items-center gap-1 rounded-full px-2.5 py-1 hover:bg-accent"
              >
                <Share2 className="h-4 w-4" />
              </button>
              <Link to={`/posts/${post.id}`} className="ml-auto text-muted-foreground hover:underline">
                Открыть
              </Link>
            </div>

            {/* Edit/Delete owner */}
            {isOwner && !editing && (
              <div className="mt-2 flex gap-2 text-xs">
                <button onClick={() => setEditing(true)} className="text-muted-foreground hover:underline">
                  Редактировать
                </button>
                {!confirmDelete ? (
                  <button onClick={() => setConfirmDelete(true)} className="text-red-500 hover:underline">
                    Удалить
                  </button>
                ) : (
                  <span className="flex gap-1">
                    <button onClick={() => deleteMut.mutate()} className="text-red-600 font-medium">
                      Подтвердить
                    </button>
                    <button onClick={() => setConfirmDelete(false)} className="text-muted-foreground">
                      Отмена
                    </button>
                  </span>
                )}
              </div>
            )}
            {deleteMut.isError && <p className="text-xs text-red-500">{(deleteMut.error as Error).message}</p>}

            {showComments && <CommentSection postId={post.id} onCountChange={onUpdated} />}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
