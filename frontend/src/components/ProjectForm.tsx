import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { X } from "lucide-react";

const schema = z.object({
  name: z.string().min(1, "Required").max(150),
  description: z.string().min(1, "Required").max(2000),
  github_url: z.string().max(512).optional().or(z.literal("")),
  demo_url: z.string().max(512).optional().or(z.literal("")),
  status: z.enum(["idea", "in_progress", "completed", "archived"]),
});

export type ProjectFormValues = z.infer<typeof schema> & { technologies: string[] };

export function ProjectForm({ defaultValues, onSubmit, onCancel, isSubmitting }: {
  defaultValues?: Partial<ProjectFormValues>;
  onSubmit: (v: ProjectFormValues) => void;
  onCancel?: () => void;
  isSubmitting?: boolean;
}) {
  const [techs, setTechs] = useState<string[]>(defaultValues?.technologies ?? []);
  const [techInput, setTechInput] = useState("");

  const { register, handleSubmit, formState: { errors } } = useForm<z.infer<typeof schema>>({
    resolver: zodResolver(schema),
    defaultValues: {
      name: defaultValues?.name ?? "",
      description: defaultValues?.description ?? "",
      github_url: defaultValues?.github_url ?? "",
      demo_url: defaultValues?.demo_url ?? "",
      status: (defaultValues?.status as any) ?? "idea",
    },
  });

  const addTech = () => {
    const t = techInput.trim();
    if (!t) return;
    if (t.length > 50) return;
    if (techs.length >= 20) return;
    if (techs.some((x) => x.toLowerCase() === t.toLowerCase())) return;
    setTechs([...techs, t]);
    setTechInput("");
  };

  const removeTech = (t: string) => setTechs(techs.filter((x) => x !== t));

  const submit = (values: z.infer<typeof schema>) => {
    onSubmit({ ...values, technologies: techs });
  };

  return (
    <Card>
      <CardContent className="p-4 space-y-4">
        <form onSubmit={handleSubmit(submit)} className="space-y-4">
          <div className="space-y-1">
            <label className="text-xs font-medium">Name *</label>
            <input {...register("name")} placeholder="Bailanysta" className="w-full rounded-xl border bg-background px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-ring" />
            {errors.name && <p className="text-xs text-red-500">{errors.name.message}</p>}
          </div>
          <div className="space-y-1">
            <label className="text-xs font-medium">Description * (max 2000)</label>
            <textarea {...register("description")} rows={4} placeholder="Social platform for IT communities..." className="w-full rounded-xl border bg-background px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-ring" />
            {errors.description && <p className="text-xs text-red-500">{errors.description.message}</p>}
          </div>
          <div className="space-y-2">
            <label className="text-xs font-medium">Technologies (max 20, 50 chars each)</label>
            <div className="flex flex-wrap gap-1.5">
              {techs.map((t) => (
                <Badge key={t} className="gap-1 pr-1">
                  {t}
                  <button type="button" onClick={() => removeTech(t)} className="ml-1 rounded-full p-0.5 hover:bg-accent"><X className="h-3 w-3" /></button>
                </Badge>
              ))}
            </div>
            <div className="flex gap-2">
              <input
                value={techInput}
                onChange={(e) => setTechInput(e.target.value)}
                onKeyDown={(e) => { if (e.key === "Enter") { e.preventDefault(); addTech(); } }}
                placeholder="Add technology and press Enter"
                className="flex-1 rounded-xl border bg-background px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-ring"
                maxLength={50}
              />
              <Button type="button" variant="outline" size="sm" onClick={addTech} disabled={!techInput.trim() || techs.length >= 20}>Add</Button>
            </div>
          </div>
          <div className="space-y-1">
            <label className="text-xs font-medium">GitHub URL (must be https://github.com/...)</label>
            <input {...register("github_url")} placeholder="https://github.com/username/repo" className="w-full rounded-xl border bg-background px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-ring" />
            {errors.github_url && <p className="text-xs text-red-500">{errors.github_url.message as string}</p>}
          </div>
          <div className="space-y-1">
            <label className="text-xs font-medium">Demo URL (https://...)</label>
            <input {...register("demo_url")} placeholder="https://example.com" className="w-full rounded-xl border bg-background px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-ring" />
            {errors.demo_url && <p className="text-xs text-red-500">{errors.demo_url.message as string}</p>}
          </div>
          <div className="space-y-1">
            <label className="text-xs font-medium">Status</label>
            <select {...register("status")} className="w-full rounded-xl border bg-background px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-ring">
              <option value="idea">Idea</option>
              <option value="in_progress">In Progress</option>
              <option value="completed">Completed</option>
              <option value="archived">Archived</option>
            </select>
            {errors.status && <p className="text-xs text-red-500">{errors.status.message}</p>}
          </div>
          <div className="flex gap-2">
            <Button type="submit" size="sm" disabled={isSubmitting}>{isSubmitting ? "Saving..." : "Save"}</Button>
            {onCancel && <Button type="button" variant="outline" size="sm" onClick={onCancel}>Cancel</Button>}
          </div>
        </form>
      </CardContent>
    </Card>
  );
}
