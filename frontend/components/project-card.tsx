import type { MatchedProject } from "@/lib/matcher"
import { Badge } from "@/components/ui/badge"
import { Briefcase, User, Calendar } from "lucide-react"

interface ProjectCardProps {
  project: MatchedProject
  rank: number
}

export function ProjectCard({ project, rank }: ProjectCardProps) {
  const scorePercent = Math.round(project.score * 100)

  return (
    <div className="group rounded-xl border border-border bg-card p-6 transition-all duration-200 hover:border-primary/30 hover:shadow-md">
      <div className="flex items-start gap-4">
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-primary/10 text-primary font-semibold text-sm">
          {rank}
        </div>
        <div className="flex-1 min-w-0 space-y-3">
          {/* Title + score */}
          <div className="flex items-start justify-between gap-3">
            <div className="min-w-0">
              <div className="flex items-center gap-2">
                <Briefcase className="h-4 w-4 text-primary shrink-0" />
                <h3 className="font-semibold text-foreground text-base leading-tight">
                  {project.name}
                </h3>
              </div>
            </div>
            <div className="shrink-0">
              <span className="inline-flex items-center rounded-full bg-accent/15 px-2.5 py-0.5 text-xs font-semibold text-accent">
                {scorePercent}% match
              </span>
            </div>
          </div>

          {/* Profile name + date */}
          <div className="flex flex-wrap items-center gap-x-4 gap-y-1">
            <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
              <User className="h-3.5 w-3.5" />
              <span className="font-medium text-foreground">
                {project.profileName}
              </span>
            </div>
            {project.startDate && (
              <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                <Calendar className="h-3.5 w-3.5" />
                <span>{project.startDate}</span>
              </div>
            )}
          </div>

          {/* Description */}
          {project.description && (
            <p className="text-sm text-muted-foreground leading-relaxed line-clamp-4">
              {project.description}
            </p>
          )}

          {/* Score bar */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between">
              <span className="text-xs text-muted-foreground">Relevance</span>
              <span className="text-xs font-medium text-foreground">
                {scorePercent}%
              </span>
            </div>
            <div className="h-1.5 w-full rounded-full bg-muted overflow-hidden">
              <div
                className="h-full rounded-full bg-primary transition-all duration-700 ease-out"
                style={{ width: `${Math.max(scorePercent, 2)}%` }}
              />
            </div>
          </div>

          {/* Matched keywords */}
          {project.matchedKeywords.length > 0 && (
            <div className="flex flex-wrap gap-1.5">
              {project.matchedKeywords.map((keyword) => (
                <Badge
                  key={keyword}
                  variant="secondary"
                  className="text-xs font-normal"
                >
                  {keyword}
                </Badge>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
