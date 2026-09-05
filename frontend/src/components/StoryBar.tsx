import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { storiesApi, StoryGroup } from "@/api/stories";
import { useAuth } from "@/stores/auth";
import { useState } from "react";
import { Button } from "@/components/ui/button";

export function StoryBar({ onSelect }: { onSelect: (group: StoryGroup, idx: number) => void }) {
  const { user } = useAuth();
  const qc = useQueryClient();
  const query = useQuery({ queryKey: ["stories"], queryFn: () => storiesApi.list() });
  const [showCreate, setShowCreate] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [text, setText] = useState("");
  const [preview, setPreview] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const createMut = useMutation({
    mutationFn: () => {
      if (!file) throw new Error("Выбери файл");
      return storiesApi.create(file, text || undefined);
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["stories"] });
      setShowCreate(false);
      setFile(null);
      setPreview(null);
      setText("");
      setError(null);
    },
    onError: (e: any) => setError(e.message),
  });

  const handleFile = (f: File | null) => {
    if (!f) return;
    setFile(f);
    setPreview(URL.createObjectURL(f));
  };

  return (
    <div className="space-y-3">
      <div className="flex gap-3 overflow-x-auto pb-2">
        <div className="flex flex-col items-center gap-1 shrink-0">
          <button
            onClick={() => setShowCreate((v) => !v)}
            className="flex h-16 w-16 items-center justify-center rounded-full border-2 border-dashed bg-card text-xl"
          >
            +
          </button>
          <span className="text-[11px]">My Story</span>
        </div>

        {query.isPending && <span className="text-xs text-muted-foreground">Загрузка...</span>}
        {query.data?.map((group) => (
          <button key={group.author?.id} onClick={() => onSelect(group, 0)} className="flex flex-col items-center gap-1 shrink-0">
            <div className="h-16 w-16 rounded-full p-[2px] bg-gradient-to-br from-violet-500 to-sky-500">
              <div className="h-full w-full rounded-full bg-card flex items-center justify-center overflow-hidden">
                {group.author?.avatar_url ? (
                  <img src={storiesApi.resolveUrl(group.author.avatar_url)!} alt={group.author.username} className="h-full w-full object-cover" />
                ) : (
                  <span className="font-bold">{group.author?.username.slice(0, 1).toUpperCase()}</span>
                )}
              </div>
            </div>
            <span className="text-[11px] truncate w-16 text-center">{group.author?.username}</span>
            <span className="text-[10px] text-muted-foreground">{group.stories.length}</span>
          </button>
        ))}
      </div>

      {showCreate && (
        <div className="rounded-2xl border bg-card p-4 space-y-3">
          <h3 className="text-sm font-semibold">Создать Story</h3>
          <input type="file" accept="image/jpeg,image/png,image/webp,video/mp4,video/webm" onChange={(e) => handleFile(e.target.files?.[0] || null)} />
          {preview && file?.type.startsWith("image") && <img src={preview} alt="preview" className="h-40 w-full object-cover rounded-xl border" />}
          {preview && file?.type.startsWith("video") && <video src={preview} controls className="h-40 w-full rounded-xl border" />}
          {file && <p className="text-xs text-muted-foreground">{file.name} · {(file.size / 1024 / 1024).toFixed(2)} MB</p>}
          <input value={text} onChange={(e) => setText(e.target.value)} placeholder="Текст (необязательно, до 2000)" maxLength={2000} className="w-full rounded-xl border bg-background px-3 py-2 text-sm" />
          {error && <p className="text-xs text-red-500">{error}</p>}
          <div className="flex gap-2">
            <Button size="sm" onClick={() => createMut.mutate()} disabled={createMut.isPending || !file}>
              {createMut.isPending ? "Создание..." : "Опубликовать"}
            </Button>
            <Button variant="outline" size="sm" onClick={() => setShowCreate(false)}>
              Отмена
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
