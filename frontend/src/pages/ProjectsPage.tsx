import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { projectsApi, ProjectRead } from "@/api/projects";
import { ProjectCard } from "@/components/ProjectCard";
import { ProjectForm, ProjectFormValues } from "@/components/ProjectForm";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/stores/auth";

export function ProjectsPage() {
  const { user } = useAuth();
  const qc = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState<ProjectRead | null>(null);
  const [imageUploading, setImageUploading] = useState<string | null>(null);

  // Global showcase: fetch current user's projects for now, plus all? For MVP show current user's projects + if no user show empty. Could also search.
  // We'll show authenticated user's projects as showcase; for global feed we could aggregate via search.
  const myQuery = useQuery({ queryKey: ["projects-my"], queryFn: () => projectsApi.listMy({ limit: 50 }), enabled: !!user });

  const createMut = useMutation({
    mutationFn: (vals: ProjectFormValues) => projectsApi.create({ name: vals.name, description: vals.description, technologies: vals.technologies, github_url: vals.github_url || null, demo_url: vals.demo_url || null, status: vals.status }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["projects-my"] }); qc.invalidateQueries({ queryKey: ["projects-search"] }); setShowForm(false); },
  });

  const updateMut = useMutation({
    mutationFn: (vals: ProjectFormValues) => projectsApi.update(editing!.id, { name: vals.name, description: vals.description, technologies: vals.technologies, github_url: vals.github_url || null, demo_url: vals.demo_url || null, status: vals.status }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["projects-my"] }); setEditing(null); },
  });

  const deleteMut = useMutation({
    mutationFn: (id: string) => projectsApi.delete(id),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["projects-my"] }); },
  });

  const handleImage = async (id: string, file: File) => {
    setImageUploading(id);
    try {
      await projectsApi.uploadImage(id, file);
      qc.invalidateQueries({ queryKey: ["projects-my"] });
    } catch (e) { /* ignore */ } finally { setImageUploading(null); }
  };

  if (!user) return <div className="text-center text-sm text-muted-foreground py-12">Войдите, чтобы видеть проекты</div>;

  const projects = myQuery.data ?? [];

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-lg font-semibold">Projects</h1>
        <Button size="sm" onClick={() => { setEditing(null); setShowForm((v) => !v); }}>{showForm ? "Close" : "Add project"}</Button>
      </div>

      {showForm && <ProjectForm onSubmit={(v) => createMut.mutate(v)} onCancel={() => setShowForm(false)} isSubmitting={createMut.isPending} />}
      {editing && <ProjectForm defaultValues={{ ...editing, github_url: editing.github_url ?? "", demo_url: editing.demo_url ?? "" }} onSubmit={(v) => updateMut.mutate(v)} onCancel={() => setEditing(null)} isSubmitting={updateMut.isPending} />}

      {myQuery.isPending ? (
        <div className="grid gap-4 md:grid-cols-2">
          <Skeleton className="h-64 rounded-[20px]" /><Skeleton className="h-64 rounded-[20px]" />
        </div>
      ) : projects.length === 0 ? (
        <div className="text-center py-12 border rounded-[20px] bg-card">
          <p className="text-sm font-medium">No projects yet</p>
          <p className="text-xs text-muted-foreground mt-1">Add your first project</p>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {projects.map((p) => (
            <div key={p.id} className="space-y-2">
              <ProjectCard project={p} isOwner onEdit={() => { setShowForm(false); setEditing(p); window.scrollTo({ top: 0, behavior: "smooth" }); }} onDelete={() => { if (confirm("Delete project?")) deleteMut.mutate(p.id); }} />
              <label className="inline-flex cursor-pointer items-center rounded-xl border px-3 py-1.5 text-xs font-medium hover:bg-accent">
                {imageUploading === p.id ? "Uploading..." : "Upload image"}
                <input type="file" accept="image/jpeg,image/png,image/webp" className="hidden" onChange={(e) => e.target.files?.[0] && handleImage(p.id, e.target.files[0])} disabled={imageUploading === p.id} />
              </label>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
