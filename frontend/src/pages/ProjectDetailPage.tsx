import { useParams, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { projectsApi } from "@/api/projects";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import { Github, ExternalLink } from "lucide-react";

const statusLabel: Record<string, string> = { idea: "Idea", in_progress: "In Progress", completed: "Completed", archived: "Archived" };

export function ProjectDetailPage() {
  const { projectId } = useParams();
  const query = useQuery({ queryKey: ["project", projectId], queryFn: () => projectsApi.get(projectId!), enabled: !!projectId });

  if (query.isPending) {
    return <div className="mx-auto max-w-2xl space-y-3"><Skeleton className="h-64 w-full rounded-2xl" /><Skeleton className="h-24 w-full rounded-2xl" /></div>;
  }
  if (query.isError || !query.data) {
    return <div className="mx-auto max-w-2xl text-center py-12 space-y-2"><p className="text-sm font-medium">Project not found</p><Link to="/projects" className="text-xs underline">Back to projects</Link></div>;
  }
  const p = query.data;
  const img = projectsApi.resolveImage(p.image_url);
  return (
    <div className="mx-auto max-w-2xl space-y-6">
      {img ? <img src={img} alt={p.name} className="w-full h-72 object-cover rounded-[24px] border" /> : <div className="w-full h-48 rounded-[24px] bg-gradient-to-br from-violet-500 via-indigo-500 to-sky-500" />}
      <div className="space-y-3">
        <div className="flex items-center gap-2">
          <h1 className="text-xl font-semibold">{p.name}</h1>
          <Badge>{statusLabel[p.status] ?? p.status}</Badge>
        </div>
        {p.owner && <Link to={`/profile/${p.owner.username}`} className="text-xs text-muted-foreground hover:underline">by @{p.owner.username}</Link>}
        <p className="text-sm leading-relaxed whitespace-pre-wrap">{p.description}</p>
        {p.technologies.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {p.technologies.map((t) => <Badge key={t}>{t}</Badge>)}
          </div>
        )}
        <div className="flex gap-2">
          {p.github_url && <a href={p.github_url} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-1.5 rounded-xl border px-3 py-1.5 text-xs font-medium hover:bg-accent"><Github className="h-3.5 w-3.5" /> GitHub</a>}
          {p.demo_url && <a href={p.demo_url} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-1.5 rounded-xl bg-foreground px-3 py-1.5 text-xs font-medium text-background"><ExternalLink className="h-3.5 w-3.5" /> Live Demo</a>}
        </div>
      </div>
    </div>
  );
}
