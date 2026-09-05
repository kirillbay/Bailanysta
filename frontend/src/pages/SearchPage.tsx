import { useState, useEffect } from "react";
import { useSearchParams, Link } from "react-router-dom";
import { searchApi, SearchResult } from "@/api/search";
import { postsApi } from "@/api/posts";
import { PostCard } from "@/components/PostCard";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";

function useDebounce<T>(value: T, delay: number) {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const id = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(id);
  }, [value, delay]);
  return debounced;
}

export function SearchPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const qParam = searchParams.get("q") || "";
  const typeParam = (searchParams.get("type") as any) || "all";
  const [q, setQ] = useState(qParam);
  const debounced = useDebounce(q, 400);
  const [tab, setTab] = useState<"all" | "users" | "posts" | "hashtags" | "projects">(typeParam);
  const [result, setResult] = useState<SearchResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setTab(typeParam as any);
  }, [typeParam]);

  useEffect(() => {
    if (debounced.trim() === "") {
      setResult(null);
      return;
    }
    setLoading(true);
    setError(null);
    searchApi
      .search(debounced.trim(), tab, 20, 0)
      .then((r) => {
        setResult(r);
        setSearchParams({ q: debounced.trim(), type: tab });
      })
      .catch((e: any) => setError(e.message))
      .finally(() => setLoading(false));
  }, [debounced, tab]);

  const handleTab = (t: typeof tab) => {
    setTab(t);
    setSearchParams({ q: debounced.trim() || qParam, type: t });
    // trigger search immediately
    if ((debounced.trim() || qParam).trim()) {
      setLoading(true);
      searchApi
        .search((debounced.trim() || qParam).trim(), t, 20, 0)
        .then(setResult)
        .catch((e: any) => setError(e.message))
        .finally(() => setLoading(false));
    }
  };

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div className="space-y-3">
        <h1 className="text-xl font-semibold">Поиск</h1>
        <div className="flex gap-2">
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="python, #python, Kirill, React"
            className="flex-1 rounded-xl border bg-background px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-ring"
            onKeyDown={(e) => e.key === "Enter" && setResult(null)}
          />
        </div>
        <div className="flex gap-2 flex-wrap">
          {(["all", "users", "posts", "hashtags", "projects"] as const).map((t) => (
            <button
              key={t}
              onClick={() => handleTab(t)}
              className={`rounded-full px-3 py-1 text-xs font-medium border ${tab === t ? "bg-foreground text-background" : "bg-card hover:bg-accent"}`}
            >
              {t}
            </button>
          ))}
        </div>
      </div>

      {!debounced.trim() && !result && <p className="text-sm text-muted-foreground">Введи запрос — попробуй python, #python, Kirill</p>}
      {loading && <Skeleton className="h-32 w-full rounded-2xl" />}
      {error && <p className="text-sm text-red-500">{error}</p>}
      {result && !loading && (
        <div className="space-y-6">
          {(tab === "all" || tab === "users") && (
            <div className="space-y-2">
              <h2 className="text-sm font-semibold">Люди ({result.users.length})</h2>
              {result.users.length === 0 ? (
                <p className="text-xs text-muted-foreground">Никого не нашли</p>
              ) : (
                result.users.map((u) => (
                  <Link key={u.id} to={`/profile/${u.username}`} className="flex items-center gap-3 rounded-xl border bg-card p-3 hover:bg-accent">
                    <div className="flex h-8 w-8 items-center justify-center rounded-full bg-foreground text-background text-xs font-bold">
                      {u.username.slice(0, 1).toUpperCase()}
                    </div>
                    <div>
                      <p className="text-sm font-medium">{u.display_name || u.username}</p>
                      <p className="text-xs text-muted-foreground">@{u.username} · {u.followers_count} followers</p>
                    </div>
                  </Link>
                ))
              )}
            </div>
          )}
          {(tab === "all" || tab === "posts") && (
            <div className="space-y-2">
              <h2 className="text-sm font-semibold">Посты ({result.posts.length})</h2>
              {result.posts.length === 0 ? <p className="text-xs text-muted-foreground">Постов не нашли</p> : result.posts.map((p) => <PostCard key={p.id} post={p} />)}
            </div>
          )}
          {(tab === "all" || tab === "hashtags") && (
            <div className="space-y-2">
              <h2 className="text-sm font-semibold">Хештеги ({result.hashtags.length})</h2>
              {result.hashtags.length === 0 ? (
                <p className="text-xs text-muted-foreground">Хештегов не нашли</p>
              ) : (
                result.hashtags.map((h) => (
                  <Link key={h.id} to={`/hashtags/${h.name}`} className="block rounded-xl border bg-card p-3 hover:bg-accent">
                    <p className="text-sm font-medium">#{h.name}</p>
                    <p className="text-xs text-muted-foreground">{h.posts_count} постов</p>
                  </Link>
                ))
              )}
            </div>
          )}
          {(tab === "all" || tab === "projects") && (
            <div className="space-y-2">
              <h2 className="text-sm font-semibold">Проекты ({result.projects?.length ?? 0})</h2>
              {(result.projects?.length ?? 0) === 0 ? (
                <p className="text-xs text-muted-foreground">Проектов не нашли</p>
              ) : (
                result.projects.map((p) => (
                  <Link key={p.id} to={`/projects/${p.id}`} className="block rounded-xl border bg-card p-3 hover:bg-accent space-y-1">
                    <p className="text-sm font-medium">{p.name}</p>
                    <p className="text-xs text-muted-foreground line-clamp-2">{p.description}</p>
                    {p.technologies?.length > 0 && <p className="text-[11px] text-muted-foreground">{p.technologies.join(" · ")}</p>}
                  </Link>
                ))
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
