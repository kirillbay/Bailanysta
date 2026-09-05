import { StoryGroup, storiesApi } from "@/api/stories";
import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { useQueryClient } from "@tanstack/react-query";

export function StoryViewer({ group, startIdx, onClose }: { group: StoryGroup; startIdx: number; onClose: () => void }) {
  const [idx, setIdx] = useState(startIdx);
  const qc = useQueryClient();
  const story = group.stories[idx];

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
      if (e.key === "ArrowRight") setIdx((i) => Math.min(i + 1, group.stories.length - 1));
      if (e.key === "ArrowLeft") setIdx((i) => Math.max(i - 1, 0));
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [group.stories.length, onClose]);

  const remaining = () => {
    const exp = new Date(story.expires_at).getTime();
    const now = Date.now();
    const diff = exp - now;
    if (diff <= 0) return "истёк";
    const h = Math.floor(diff / 3600000);
    const m = Math.floor((diff % 3600000) / 60000);
    return `${h}h ${m}m`;
  };

  const handleDelete = async () => {
    try {
      await storiesApi.remove(story.id);
      qc.invalidateQueries({ queryKey: ["stories"] });
      if (group.stories.length === 1) onClose();
      else if (idx >= group.stories.length - 1) setIdx((i) => i - 1);
    } catch (e) {
      alert((e as Error).message);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-4" onClick={onClose}>
      <div className="relative w-full max-w-md rounded-2xl bg-card overflow-hidden" onClick={(e) => e.stopPropagation()}>
        <div className="flex items-center justify-between p-3 border-b">
          <div className="flex items-center gap-2">
            <span className="text-sm font-semibold">@{group.author?.username}</span>
            <span className="text-xs text-muted-foreground">{new Date(story.created_at).toLocaleString("ru-RU")}</span>
            <span className="text-xs text-muted-foreground">· {remaining()}</span>
          </div>
          <button onClick={onClose} className="text-sm px-2 py-1 rounded-lg hover:bg-accent">
            ✕
          </button>
        </div>

        <div className="bg-black flex items-center justify-center min-h-[300px]">
          {story.media_type === "image" ? (
            <img src={storiesApi.resolveUrl(story.media_url)!} alt="story" className="max-h-[60vh] w-full object-contain" />
          ) : story.media_type === "video" ? (
            <video src={storiesApi.resolveUrl(story.media_url)!} controls autoPlay className="max-h-[60vh] w-full" />
          ) : (
            <p className="text-white p-6 text-center">{story.text}</p>
          )}
        </div>

        {story.text && <p className="p-3 text-sm whitespace-pre-wrap">{story.text}</p>}

        <div className="flex items-center justify-between p-3 border-t">
          <div className="flex gap-2">
            <Button size="sm" variant="outline" disabled={idx === 0} onClick={() => setIdx((i) => i - 1)}>
              Назад
            </Button>
            <Button size="sm" variant="outline" disabled={idx === group.stories.length - 1} onClick={() => setIdx((i) => i + 1)}>
              Далее
            </Button>
          </div>
          <Button size="sm" variant="ghost" onClick={handleDelete}>
            Удалить
          </Button>
        </div>
        <p className="text-center text-xs text-muted-foreground pb-2">
          {idx + 1} / {group.stories.length}
        </p>
      </div>
    </div>
  );
}
