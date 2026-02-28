export interface RawProject {
  title: string
  start_date?: string
  description?: string | null
}

export interface LinkedInProfile {
  id: string
  name: string
  city?: string
  projects?: RawProject[]
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
 * Extract all projects from every profile in the JSON array,
 * flattening them into a single list with the owner's name attached.
 */
export function extractAllProjects(profiles: LinkedInProfile[]): Project[] {
  const projects: Project[] = []
  for (const profile of profiles) {
    if (!profile.projects || profile.projects.length === 0) continue
    for (const p of profile.projects) {
      projects.push({
        name: p.title,
        description: p.description ?? "",
        profileName: profile.name,
        profileId: profile.id,
        startDate: p.start_date,
      })
    }
  }
  return projects
}

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
 * Compute TF (term frequency) for a list of tokens.
 */
function computeTF(tokens: string[]): Map<string, number> {
  const tf = new Map<string, number>()
  for (const token of tokens) {
    tf.set(token, (tf.get(token) || 0) + 1)
  }
  const total = tokens.length
  for (const [key, val] of tf) {
    tf.set(key, val / total)
  }
  return tf
}

/**
 * Compute IDF (inverse document frequency) across all documents.
 */
function computeIDF(documents: string[][]): Map<string, number> {
  const idf = new Map<string, number>()
  const n = documents.length

  for (const doc of documents) {
    const uniqueTokens = new Set(doc)
    for (const token of uniqueTokens) {
      idf.set(token, (idf.get(token) || 0) + 1)
    }
  }

  for (const [key, val] of idf) {
    idf.set(key, Math.log((n + 1) / (val + 1)) + 1)
  }

  return idf
}

/**
 * Compute cosine similarity between two TF-IDF vectors.
 */
function cosineSimilarity(
  vecA: Map<string, number>,
  vecB: Map<string, number>
): number {
  let dotProduct = 0
  let normA = 0
  let normB = 0

  for (const [key, val] of vecA) {
    normA += val * val
    if (vecB.has(key)) {
      dotProduct += val * vecB.get(key)!
    }
  }

  for (const [, val] of vecB) {
    normB += val * val
  }

  if (normA === 0 || normB === 0) return 0
  return dotProduct / (Math.sqrt(normA) * Math.sqrt(normB))
}

/**
 * Find the top keywords contributing to the match.
 */
function findMatchedKeywords(
  essayTokens: string[],
  projectTokens: string[],
  idf: Map<string, number>
): string[] {
  const essaySet = new Set(essayTokens)
  const projectSet = new Set(projectTokens)
  const overlapping: { word: string; weight: number }[] = []

  for (const word of essaySet) {
    if (projectSet.has(word)) {
      overlapping.push({ word, weight: idf.get(word) || 1 })
    }
  }

  return overlapping
    .sort((a, b) => b.weight - a.weight)
    .slice(0, 8)
    .map((o) => o.word)
}

/**
 * Match essay text against a flat list of projects.
 * Returns the top-k matching projects sorted by relevance.
 */
export function matchProjects(
  essayText: string,
  projects: Project[],
  topK: number = 3
): MatchedProject[] {
  const essayTokens = tokenize(essayText)

  if (essayTokens.length === 0) {
    return []
  }

  const projectTokensList = projects.map((p) =>
    tokenize(`${p.name} ${p.description}`)
  )

  // Build corpus: essay + all project descriptions
  const allDocuments = [essayTokens, ...projectTokensList]
  const idf = computeIDF(allDocuments)

  // Compute TF-IDF for essay
  const essayTF = computeTF(essayTokens)
  const essayTFIDF = new Map<string, number>()
  for (const [key, val] of essayTF) {
    essayTFIDF.set(key, val * (idf.get(key) || 1))
  }

  // Compute TF-IDF for each project and calculate similarity
  const results: MatchedProject[] = projects.map((project, idx) => {
    const projTF = computeTF(projectTokensList[idx])
    const projTFIDF = new Map<string, number>()
    for (const [key, val] of projTF) {
      projTFIDF.set(key, val * (idf.get(key) || 1))
    }

    const score = cosineSimilarity(essayTFIDF, projTFIDF)
    const matchedKeywords = findMatchedKeywords(
      essayTokens,
      projectTokensList[idx],
      idf
    )

    return {
      ...project,
      score,
      matchedKeywords,
    }
  })

  return results
    .sort((a, b) => b.score - a.score)
    .slice(0, topK)
    .filter((r) => r.score > 0)
}
