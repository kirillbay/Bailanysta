import { useParams, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { postsApi } from "@/api/posts";
import { PostCard } from "@/components/PostCard";
import { Skeleton } from "@/components/ui/skeleton";

export function PostDetailPage() {
  const { postId } = useParams();
  const query = useQuery({
    queryKey: ["post", postId],
    queryFn: () => postsApi.get(postId!),
    enabled: !!postId,
  });

  if (query.isPending) {
    return (
      <div className="mx-auto max-w-2xl space-y-4">
        <Skeleton className="h-40 w-full rounded-2xl" />
      </div>
    );
  }

  if (query.isError) {
    return (
      <div className="mx-auto max-w-2xl text-center py-12 space-y-3">
        <p className="text-sm font-medium">Пост не найден</p>
        <p className="text-xs text-muted-foreground">Возможно, он был удалён.</p>
        <Link to="/" className="inline-block rounded-xl bg-foreground px-4 py-2 text-sm text-background">На главную</Link>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl space-y-4">
      <PostCard post={query.data!} />
    </div>
  );
}
