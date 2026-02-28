export interface RawProject {
  title: string
  start_date?: string
  description?: string | null
}

export interface LinkedInProfile {
  id?: string
  name: string
  city?: string
  projects?: RawProject[] | string
}

export interface Project {
  name: string
  description: string
  profileName: string
  profileId: string
  startDate?: string
}

export interface MatchedProject extends Project {
  score: number
  matchedKeywords: string[]
}

/**
 * Parse a Python-style list string into a JSON array.
 * Handles single quotes, None values, True/False, and embedded apostrophes.
 *
 * Strategy: walk character-by-character to correctly distinguish
 * structural single quotes (delimiters) from apostrophes within values.
 */
function parsePythonList(raw: string): RawProject[] {
  try {
    // First pass: replace Python keywords outside of string values
    let s = raw.trim()

    // Walk through and convert single-quoted strings to double-quoted
    let result = ""
    let i = 0
    while (i < s.length) {
      if (s[i] === "'") {
        // This is a structural opening single quote — find the closing one
        // A closing quote is a ' followed by a structural char: , ] } :
        result += '"'
        i++
        let value = ""
        while (i < s.length) {
          if (
            s[i] === "'" &&
            (i + 1 >= s.length || /[,\]\}:\s]/.test(s[i + 1]))
          ) {
            // Closing structural quote
            break
          }
          // Escape any double quotes inside the value
          if (s[i] === '"') {
            value += '\\"'
          } else if (s[i] === "\\") {
            value += "\\\\"
            // skip next char too
            i++
            if (i < s.length) value += s[i]
          } else {
            value += s[i]
          }
          i++
        }
        result += value + '"'
        i++ // skip closing quote
      } else {
        result += s[i]
        i++
      }
    }

    // Replace Python keywords
    result = result
      .replace(/\bNone\b/g, "null")
      .replace(/\bTrue\b/g, "true")
      .replace(/\bFalse\b/g, "false")

    const parsed = JSON.parse(result)
    if (Array.isArray(parsed)) {
      return parsed.filter(
        (item: RawProject | null) => item !== null && item !== undefined
      )
    }
    return []
  } catch (err) {
    console.error("[v0] parsePythonList failed:", err, "raw length:", raw.length)
    return []
  }
}

/**
 * Extract all projects from every profile in the JSON array,
 * flattening them into a single list with the owner's name attached.
 * Handles projects as either a JSON array or a Python-style string.
 */
export function extractAllProjects(profiles: LinkedInProfile[]): Project[] {
  const projects: Project[] = []
  for (const profile of profiles) {
    if (!profile.projects) continue

    let projectList: RawProject[]

    if (typeof profile.projects === "string") {
      // Projects field is a Python-style string, parse it
      projectList = parsePythonList(profile.projects)
    } else if (Array.isArray(profile.projects)) {
      projectList = profile.projects.filter(
        (p): p is RawProject => p !== null && p !== undefined
      )
    } else {
      continue
    }

    if (projectList.length === 0) continue

    for (const p of projectList) {
      if (!p || !p.title) continue
      projects.push({
        name: p.title,
        description: p.description ?? "",
        profileName: profile.name,
        profileId: profile.id ?? profile.name,
        startDate: p.start_date,
      })
    }
  }
  return projects
}

/* ------------------------------------------------------------------ */
/*  Shared helpers                                                     */
/* ------------------------------------------------------------------ */

/**
 * Tokenize text into lowercase words, removing punctuation and stop words.
 */
function tokenize(text: string): string[] {
  const stopWords = new Set([
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "it", "that", "this", "was", "are",
    "be", "has", "had", "have", "will", "would", "could", "should", "may",
    "might", "shall", "can", "do", "does", "did", "not", "so", "if", "then",
    "than", "too", "very", "just", "about", "above", "after", "again",
    "all", "also", "am", "as", "because", "been", "before", "being",
    "below", "between", "both", "during", "each", "few", "further", "get",
    "got", "here", "how", "i", "into", "its", "let", "me", "more", "most",
    "my", "no", "nor", "now", "only", "other", "our", "out", "over", "own",
    "same", "she", "he", "some", "such", "there", "these", "they", "those",
    "through", "under", "until", "up", "us", "we", "what", "when", "where",
    "which", "while", "who", "whom", "why", "you", "your", "their",
    "using", "used", "use", "based", "make", "made", "like", "well",
    "one", "two", "first", "new", "way", "work", "working", "project",
  ])

  return text
    .toLowerCase()
    .replace(/[^a-z0-9\s-]/g, " ")
    .split(/\s+/)
    .filter((word) => word.length > 2 && !stopWords.has(word))
}

/**
 * Find shared meaningful keywords between essay and project (for display).
 */
function findSharedKeywords(
  essayText: string,
  projectText: string
): string[] {
  const essayTokens = new Set(tokenize(essayText))
  const projectTokens = tokenize(projectText)

  // Count project token frequency for weighting
  const freq = new Map<string, number>()
  for (const t of projectTokens) {
    if (essayTokens.has(t)) {
      freq.set(t, (freq.get(t) || 0) + 1)
    }
  }

  return Array.from(freq.entries())
    .sort((a, b) => b[1] - a[1])
    .slice(0, 8)
    .map(([word]) => word)
}

/* ------------------------------------------------------------------ */
/*  Cosine similarity on OpenAI embeddings                             */
/* ------------------------------------------------------------------ */

function cosineSim(a: number[], b: number[]): number {
  let dot = 0
  let normA = 0
  let normB = 0
  for (let i = 0; i < a.length; i++) {
    dot += a[i] * b[i]
    normA += a[i] * a[i]
    normB += b[i] * b[i]
  }
  if (normA === 0 || normB === 0) return 0
  return dot / (Math.sqrt(normA) * Math.sqrt(normB))
}

/**
 * Fetch embeddings from our /api/embed route.
 */
async function getEmbeddings(texts: string[]): Promise<number[][]> {
  const res = await fetch("/api/embed", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ texts }),
  })

  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(
      (err as { error?: string }).error || `Embedding request failed (${res.status})`
    )
  }

  const data = (await res.json()) as { embeddings: number[][] }
  return data.embeddings
}

/**
 * Match essay text against projects using OpenAI embeddings.
 * Calls the /api/embed route, computes cosine similarity,
 * and returns the top-k results.
 */
export async function matchProjectsWithEmbeddings(
  essayText: string,
  projects: Project[],
  topK: number = 3
): Promise<MatchedProject[]> {
  if (projects.length === 0 || !essayText.trim()) return []

  // Build text representations for each project
  const projectTexts = projects.map(
    (p) => `${p.name}. ${p.description}`.trim()
  )

  // Get all embeddings in a single request: [essay, ...projects]
  const allTexts = [essayText, ...projectTexts]
  const embeddings = await getEmbeddings(allTexts)

  const essayEmbedding = embeddings[0]
  const projectEmbeddings = embeddings.slice(1)

  // Score every project
  const scored = projects.map((project, idx) => {
    const score = cosineSim(essayEmbedding, projectEmbeddings[idx])
    const keywords = findSharedKeywords(
      essayText,
      `${project.name} ${project.description}`
    )
    return { ...project, score, matchedKeywords: keywords }
  })

  return scored
    .sort((a, b) => b.score - a.score)
    .slice(0, topK)
    .filter((r) => r.score > 0)
}
