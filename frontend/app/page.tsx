"use client"

import { useState, useCallback } from "react"
import { EssayUploader } from "@/components/essay-uploader"
import { ResultsPanel } from "@/components/results-panel"
import {
  matchProjectsWithEmbeddings,
  extractAllProjects,
  type MatchedProject,
  type Project,
  type LinkedInProfile,
} from "@/lib/matcher"
import { Loader2, FileSearch, SlidersHorizontal, AlertCircle } from "lucide-react"
import { Slider } from "@/components/ui/slider"

export default function Home() {
  const [results, setResults] = useState<MatchedProject[] | null>(null)
  const [isProcessing, setIsProcessing] = useState(false)
  const [totalProfiles, setTotalProfiles] = useState(0)
  const [totalProjects, setTotalProjects] = useState(0)
  const [topK, setTopK] = useState(3)
  const [essayText, setEssayText] = useState<string | null>(null)
  const [essayFileName, setEssayFileName] = useState<string | null>(null)
  const [allProjects, setAllProjects] = useState<Project[]>([])
  const [error, setError] = useState<string | null>(null)

  // Cache embeddings so top-K slider doesn't re-call OpenAI
  const [cachedScored, setCachedScored] = useState<MatchedProject[]>([])

  const runMatch = useCallback(
    async (text: string, k: number, projects?: Project[]) => {
      setIsProcessing(true)
      setError(null)

      try {
        let projectList = projects
        if (!projectList || projectList.length === 0) {
          const res = await fetch("/linkedinprofile.json")
          const jsonText = await res.text()
          // Support both JSON array and JSONL (newline-delimited JSON) formats
          let profiles: LinkedInProfile[]
          const trimmed = jsonText.trim()
          if (trimmed.startsWith("[")) {
            profiles = JSON.parse(trimmed)
          } else {
            profiles = trimmed
              .split("\n")
              .filter((line) => line.trim().length > 0)
              .map((line) => JSON.parse(line))
          }
          projectList = extractAllProjects(profiles)
          console.log("[v0] Parsed profiles:", profiles.length, "Extracted projects:", projectList.length)
          projectList.forEach((p, i) =>
            console.log(`[v0] Project ${i}: "${p.name}" by ${p.profileName} (desc length: ${p.description.length})`)
          )
          setAllProjects(projectList)
          setTotalProfiles(profiles.length)
          setTotalProjects(projectList.length)
        }

        // Call OpenAI embeddings and compute similarity
        const matched = await matchProjectsWithEmbeddings(
          text,
          projectList,
          // Get all scored results so we can re-slice for top-K changes
          projectList.length
        )
        setCachedScored(matched)
        setResults(matched.slice(0, k))
      } catch (err) {
        const message =
          err instanceof Error ? err.message : "An unexpected error occurred"
        setError(message)
        setResults([])
      } finally {
        setIsProcessing(false)
      }
    },
    []
  )

  const handleTextLoaded = useCallback(
    (text: string, fileName: string) => {
      setEssayText(text)
      setEssayFileName(fileName)
      setCachedScored([])
      runMatch(text, topK)
    },
    [runMatch, topK]
  )

  const handleTopKChange = useCallback(
    (value: number[]) => {
      const newK = value[0]
      setTopK(newK)

      // If we have cached scores, just re-slice — no new API call
      if (cachedScored.length > 0) {
        setResults(cachedScored.slice(0, newK))
      } else if (essayText) {
        runMatch(essayText, newK, allProjects)
      }
    },
    [essayText, runMatch, allProjects, cachedScored]
  )

  return (
    <main className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card/80 backdrop-blur-sm sticky top-0 z-10">
        <div className="mx-auto max-w-3xl px-4 sm:px-6 py-4 flex items-center gap-3">
          <div className="rounded-lg bg-primary/10 p-2">
            <FileSearch className="h-5 w-5 text-primary" />
          </div>
          <div>
            <h1 className="text-lg font-semibold text-foreground tracking-tight">
              Essay Project Matcher
            </h1>
            <p className="text-xs text-muted-foreground">
              Semantic matching powered by OpenAI embeddings
            </p>
          </div>
        </div>
      </header>

      <div className="mx-auto max-w-3xl px-4 sm:px-6 py-8 space-y-8">
        {/* Upload section */}
        <section className="space-y-4">
          <div>
            <h2 className="text-sm font-medium text-foreground">
              Upload Essay
            </h2>
            <p className="text-xs text-muted-foreground mt-0.5">
              Upload a .txt file to find semantically similar projects across
              all profiles
            </p>
          </div>
          <EssayUploader
            onTextLoaded={handleTextLoaded}
            isProcessing={isProcessing}
          />
        </section>

        {/* Top-K control */}
        {essayFileName && (
          <section className="rounded-xl border border-border bg-card p-5 space-y-4">
            <div className="flex items-center gap-2">
              <SlidersHorizontal className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm font-medium text-foreground">
                Top-K Results
              </span>
              <span className="ml-auto text-sm font-semibold text-primary tabular-nums">
                {topK}
              </span>
            </div>
            <Slider
              value={[topK]}
              onValueChange={handleTopKChange}
              min={1}
              max={10}
              step={1}
              className="w-full"
            />
            <div className="flex justify-between text-xs text-muted-foreground">
              <span>1</span>
              <span>5</span>
              <span>10</span>
            </div>
          </section>
        )}

        {/* Error */}
        {error && (
          <div className="flex items-start gap-3 rounded-xl border border-destructive/30 bg-destructive/5 p-4">
            <AlertCircle className="h-5 w-5 text-destructive shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-destructive">
                Matching failed
              </p>
              <p className="text-xs text-muted-foreground mt-1">{error}</p>
            </div>
          </div>
        )}

        {/* Loading */}
        {isProcessing && (
          <div className="flex items-center justify-center gap-3 py-12">
            <Loader2 className="h-5 w-5 animate-spin text-primary" />
            <span className="text-sm text-muted-foreground">
              Generating embeddings for {totalProjects || "all"} projects...
            </span>
          </div>
        )}

        {/* Results */}
        {!isProcessing && results !== null && !error && (
          <section>
            <ResultsPanel
              results={results}
              totalProfiles={totalProfiles}
              totalProjects={totalProjects}
            />
          </section>
        )}
      </div>
    </main>
  )
}
