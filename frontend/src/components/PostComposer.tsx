import { useState, useEffect } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { postsApi } from "@/api/posts";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { useAuth } from "@/stores/auth";

const MAX_CHARS = 10000;
const MAX_IMAGES = 4;

export function PostComposer({ onCreated }: { onCreated?: () => void }) {
  const { user } = useAuth();
  const qc = useQueryClient();
  const [content, setContent] = useState("");
  const [files, setFiles] = useState<File[]>([]);
  const [previews, setPreviews] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);

  const mutation = useMutation({
    mutationFn: () => postsApi.create(content, files),
    onSuccess: () => {
      setContent("");
      previews.forEach((u) => URL.revokeObjectURL(u));
      setFiles([]);
      setPreviews([]);
      setError(null);
      qc.invalidateQueries({ queryKey: ["posts"] });
      qc.invalidateQueries({ queryKey: ["user-posts"] });
      onCreated?.();
    },
    onError: (e: any) => setError(e.message || "Ошибка"),
  });

  const handleFiles = (list: FileList | null) => {
    if (!list) return;
    const arr = Array.from(list).slice(0, MAX_IMAGES - files.length);
    if (files.length + arr.length > MAX_IMAGES) {
      setError(`Максимум ${MAX_IMAGES} изображений`);
      return;
    }
    const newFiles = [...files, ...arr];
    setFiles(newFiles);
    const newPreviews = arr.map((f) => URL.createObjectURL(f));
    setPreviews((prev) => [...prev, ...newPreviews]);
  };

  const removeFile = (idx: number) => {
    URL.revokeObjectURL(previews[idx]);
    setFiles((prev) => prev.filter((_, i) => i !== idx));
    setPreviews((prev) => prev.filter((_, i) => i !== idx));
  };

  const remaining = MAX_CHARS - content.length;

  // Cleanup object URLs on unmount to prevent memory leak (P3)
  useEffect(() => {
    return () => {
      previews.forEach((u) => URL.revokeObjectURL(u));
    };
  }, [previews]);

  return (
    <Card>
      <CardContent className="p-4 space-y-3">
        <div className="flex gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-full bg-foreground text-background text-sm font-bold shrink-0">
            {user?.username.slice(0, 1).toUpperCase() ?? "?"}
          </div>
          <div className="flex-1 space-y-2">
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="Что нового в IT мире? #python #ai"
              rows={3}
              maxLength={MAX_CHARS}
              className="w-full rounded-xl border bg-background px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-ring"
            />
            <div className="flex items-center justify-between">
              <span className={`text-xs ${remaining < 100 ? "text-amber-600" : "text-muted-foreground"}`}>{content.length}/{MAX_CHARS}</span>
              <label className="cursor-pointer rounded-xl border px-3 py-1 text-xs hover:bg-accent">
                Добавить фото
                <input type="file" accept="image/jpeg,image/png,image/webp" multiple className="hidden" onChange={(e) => handleFiles(e.target.files)} />
              </label>
            </div>

            {previews.length > 0 && (
              <div className="grid grid-cols-2 gap-2">
                {previews.map((url, idx) => (
                  <div key={idx} className="relative">
                    <img src={url} alt="preview" className="h-32 w-full rounded-xl object-cover border" />
                    <button onClick={() => removeFile(idx)} className="absolute right-1 top-1 rounded-full bg-black/60 px-2 py-0.5 text-xs text-white">
                      ✕
                    </button>
                  </div>
                ))}
              </div>
            )}

            {error && <p className="rounded-xl bg-red-50 p-2 text-xs text-red-700 dark:bg-red-950/30">{error}</p>}

            <div className="flex justify-end">
              <Button size="sm" onClick={() => mutation.mutate()} disabled={mutation.isPending || (!content.trim() && files.length === 0) || content.length > MAX_CHARS}>
                {mutation.isPending ? "Публикация..." : "Опубликовать"}
              </Button>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
