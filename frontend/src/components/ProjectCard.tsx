import { Link } from "react-router-dom";
import { ExternalLink, Github } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { projectsApi, ProjectRead } from "@/api/projects";

const statusMap: Record<string, string> = {
  idea: "Idea",
  in_progress: "In Progress",
  completed: "Completed",
  archived: "Archived",
};

export function ProjectCard({ project, isOwner, onEdit, onDelete }: { project: ProjectRead; isOwner?: boolean; onEdit?: () => void; onDelete?: () => void }) {
  const img = projectsApi.resolveImage(project.image_url);
  const status = statusMap[project.status] ?? project.status;
  return (
    <Card className="overflow-hidden rounded-[20px] border bg-card hover:shadow-md transition-shadow">
      {img ? (
        <img src={img} alt={project.name} className="h-44 w-full object-cover" loading="lazy" />
      ) : (
        <div className="h-44 w-full bg-gradient-to-br from-violet-500 via-indigo-500 to-sky-500 flex items-center justify-center text-white font-semibold text-lg">
          {project.name.slice(0, 2).toUpperCase()}
        </div>
      )}
      <CardContent className="p-4 space-y-3">
        <div className="flex items-start justify-between gap-2">
          <Link to={`/projects/${project.id}`} className="text-sm font-semibold leading-tight hover:underline line-clamp-1">
            {project.name}
          </Link>
          <Badge className="shrink-0 text-[10px]">{status}</Badge>
        </div>
        <p className="text-xs text-muted-foreground line-clamp-2 leading-relaxed whitespace-pre-wrap">{project.description}</p>
        {project.technologies.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {project.technologies.slice(0, 6).map((t) => (
              <Badge key={t} className="text-[10px] px-2 py-0.5 rounded-full truncate max-w-[120px]">{t}</Badge>
            ))}
            {project.technologies.length > 6 && <Badge className="text-[10px]">+{project.technologies.length - 6}</Badge>}
          </div>
        )}
        <div className="flex flex-wrap gap-2 pt-1">
          {project.github_url && (
            <a href={project.github_url} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-1.5 rounded-xl border px-3 py-1.5 text-xs font-medium hover:bg-accent">
              <Github className="h-3.5 w-3.5" /> GitHub
            </a>
          )}
          {project.demo_url && (
            <a href={project.demo_url} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-1.5 rounded-xl bg-foreground px-3 py-1.5 text-xs font-medium text-background hover:opacity-90">
              Live Demo <ExternalLink className="h-3 w-3" />
            </a>
          )}
        </div>
        {isOwner && (
          <div className="flex gap-2 pt-2">
            <Button variant="outline" size="sm" onClick={onEdit}>Edit</Button>
            <Button variant="outline" size="sm" onClick={onDelete}>Delete</Button>
          </div>
        )}
        {project.owner && (
          <div className="flex items-center gap-2 pt-1 text-xs text-muted-foreground">
            <span>by</span>
            <Link to={`/profile/${project.owner.username}`} className="font-medium text-foreground hover:underline">@{project.owner.username}</Link>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
