import { buildPrompt } from "./landlord-features-prompt"

const GEMMA_API_URL =
  "https://generativelanguage.googleapis.com/v1beta/models/gemma-4-31b-it:generateContent"

export type LandlordFeatures = Record<string, number>

export async function extractLandlordFeatures(
  text: string,
  apiKey: string,
  apiBaseUrl: string = "http://localhost:3001"
): Promise<LandlordFeatures> {
  const featuresRes = await fetch(`${apiBaseUrl}/api/features`)
  if (!featuresRes.ok) {
    throw new Error(
      `Failed to fetch features: ${featuresRes.status}`
    )
  }
  const existingFeatures = (await featuresRes.json()) as {
    feature_id: string
    name: string
  }[]
  const existingKeys = existingFeatures.map((f) => f.name)

  const prompt = buildPrompt(text, existingKeys)

  const response = await fetch(`${GEMMA_API_URL}?key=${apiKey}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      contents: [{ parts: [{ text: prompt }] }],
      generationConfig: {
        temperature: 0.1,
        maxOutputTokens: 2048
      }
    })
  })

  if (!response.ok) {
    const error = await response.text()
    throw new Error(`Gemma API error ${response.status}: ${error}`)
  }

  const data = await response.json()
  const parts = data.candidates[0].content.parts
  const llm_output = parts[parts.length - 1].text

  const json = llm_output
    .replace(/^```(?:json)?\s*/i, "")
    .replace(/\s*```$/, "")
    .trim()
  const features = JSON.parse(json) as Record<string, unknown>

  for (const [key, value] of Object.entries(features)) {
    if (typeof value !== "number" || value < -1 || value > 1) {
      throw new Error(`Invalid value for feature "${key}": ${value}`)
    }
  }

  const existingKeySet = new Set(existingKeys)
  await Promise.all(
    Object.keys(features)
      .filter((key) => !existingKeySet.has(key))
      .map((key) =>
        fetch(`${apiBaseUrl}/api/features`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ name: key })
        })
      )
  )

  return features as LandlordFeatures
}
