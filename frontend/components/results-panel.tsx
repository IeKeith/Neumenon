import type { MatchedProject } from "@/lib/matcher"
import { ProjectCard } from "@/components/project-card"
import { SearchX, Users, FolderOpen } from "lucide-react"

interface ResultsPanelProps {
  results: MatchedProject[]
  totalProfiles: number
  totalProjects: number
}

export function ResultsPanel({
  results,
  totalProfiles,
  totalProjects,
}: ResultsPanelProps) {
  if (results.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center">
        <div className="rounded-full bg-muted p-4 mb-4">
          <SearchX className="h-6 w-6 text-muted-foreground" />
        </div>
        <p className="text-sm font-medium text-foreground">
          No matching projects found
        </p>
        <p className="text-xs text-muted-foreground mt-1 max-w-xs">
          Try uploading a different essay with topics that align with the
          profile projects.
        </p>
      </div>
    )
  }

  // Count unique profile names in results
  const uniqueProfiles = new Set(results.map((r) => r.profileName))

  return (
    <div className="space-y-4">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h2 className="text-lg font-semibold text-foreground">
            Matching Projects
          </h2>
          <p className="text-sm text-muted-foreground mt-0.5">
            Found across{" "}
            <span className="font-medium text-foreground">
              {uniqueProfiles.size}
            </span>{" "}
            {uniqueProfiles.size === 1 ? "profile" : "profiles"}
          </p>
        </div>
        <div className="flex items-center gap-4 text-xs text-muted-foreground shrink-0">
          <div className="flex items-center gap-1.5">
            <Users className="h-3.5 w-3.5" />
            <span>{totalProfiles} profiles</span>
          </div>
          <div className="flex items-center gap-1.5">
            <FolderOpen className="h-3.5 w-3.5" />
            <span>{totalProjects} projects</span>
          </div>
        </div>
      </div>
      <div className="space-y-3">
        {results.map((project, index) => (
          <ProjectCard
            key={`${project.profileId}-${project.name}`}
            project={project}
            rank={index + 1}
          />
        ))}
      </div>
    </div>
  )
}
