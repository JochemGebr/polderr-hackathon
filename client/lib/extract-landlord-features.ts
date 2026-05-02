const GEMMA_API_URL =
  "https://generativelanguage.googleapis.com/v1beta/models/gemma-4-31b-it:generateContent"

export type LandlordFeatures = Record<string, number>

export async function extractLandlordFeatures(
  text: string,
  apiKey: string,
  existingKeys: string[] = []
): Promise<LandlordFeatures> {
  const existingKeysSection =
    existingKeys.length > 0
      ? `\nPrefer reusing these existing keys over inventing synonyms:\n` +
        `${existingKeys.join(", ")}\n`
      : ""

  const prompt = `You are analyzing a rental applicant's text to identify traits
that landlords typically care about, or you are processing a rental description
for the same kind of traits.

Extract key-value pairs where:
- The key is a landlord concern (e.g. "cleanliness", "noise_level",
  "party_behavior", "pet_ownership", "smoking", "payment_reliability",
  "stability", "social_activity", "is_female")
- The value is a float between -1.0 and 1.0 indicating how strongly this trait
  is suggested:
  - 1.0 = very strong positive signal for landlord (e.g. extremely clean, very
    quiet)
  - 0.0 = neutral or not mentioned
  - -1.0 = very strong negative signal for landlord (e.g. loud parties, messy)

Only include traits that are actually evidenced in the text. Use snake_case
for keys.${existingKeysSection}
Respond ONLY with valid JSON, no explanation, no code fences \`\`\`. Example:
{"cleanliness": 0.8, "noise_level": -0.6, "party_behavior": -0.9}

Text to analyze:
${text}`

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

  const features = JSON.parse(llm_output) as Record<string, unknown>

  for (const [key, value] of Object.entries(features)) {
    if (typeof value !== "number" || value < -1 || value > 1) {
      throw new Error(`Invalid value for feature "${key}": ${value}`)
    }
  }

  return features as LandlordFeatures
}
