import { NextResponse } from "next/server"
import OpenAI from "openai"

const openai = new OpenAI({
  apiKey: "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",
})

/**
 * POST /api/embed
 * Body: { texts: string[] }
 * Returns: { embeddings: number[][] }
 *
 * Generates embeddings for an array of text strings using
 * OpenAI's text-embedding-3-small model.
 */
export async function POST(request: Request) {
  try {
    const { texts } = (await request.json()) as { texts: string[] }

    if (!texts || !Array.isArray(texts) || texts.length === 0) {
      return NextResponse.json(
        { error: "Missing or invalid 'texts' array in request body." },
        { status: 400 }
      )
    }

    // OpenAI supports up to 2048 inputs per request, but we batch at 100
    // to keep latency reasonable.
    const BATCH_SIZE = 100
    const allEmbeddings: number[][] = []

    for (let i = 0; i < texts.length; i += BATCH_SIZE) {
      const batch = texts.slice(i, i + BATCH_SIZE).map((t) =>
        // Trim whitespace and truncate very long texts to ~8000 tokens (~32k chars)
        t.trim().slice(0, 32000)
      )

      const response = await openai.embeddings.create({
        model: "text-embedding-3-small",
        input: batch,
      })

      // Ensure order matches input order
      const sorted = response.data.sort((a, b) => a.index - b.index)
      for (const item of sorted) {
        allEmbeddings.push(item.embedding)
      }
    }

    return NextResponse.json({ embeddings: allEmbeddings })
  } catch (error) {
    console.error("Embedding API error:", error)
    const message =
      error instanceof Error ? error.message : "Unknown error occurred"
    return NextResponse.json({ error: message }, { status: 500 })
  }
}
