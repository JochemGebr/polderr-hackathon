import assert from "node:assert/strict"
import { extractLandlordFeatures } from "./extract-landlord-features"

const apiKey = process.env.GOOGLE_AI_API_KEY
if (!apiKey) throw new Error("Set GOOGLE_AI_API_KEY env var")

const API_BASE = process.env.API_BASE_URL ?? "http://localhost:3001"

async function getFeatureNames(): Promise<Set<string>> {
  const res = await fetch(`${API_BASE}/api/features`)
  if (!res.ok) throw new Error(`GET /api/features failed: ${res.status}`)
  const features = (await res.json()) as { name: string }[]
  return new Set(features.map((f) => f.name))
}

;(async () => {
  const text = `
    I am a quiet professional who keeps the apartment spotless.
    No parties, no pets, no smoking. Stable income, have been
    renting for 5 years without missing a single payment.
  `

  const before = await getFeatureNames()
  console.log("Features before:", [...before])

  const extracted = await extractLandlordFeatures(text, apiKey, API_BASE)
  console.log("Extracted features:", extracted)

  const after = await getFeatureNames()
  console.log("Features after:", [...after])

  const newKeys = Object.keys(extracted).filter((k) => !before.has(k))
  console.log("New keys written to DB:", newKeys)

  for (const key of Object.keys(extracted)) {
    assert(
      after.has(key),
      `Expected key "${key}" to be in the database after extraction`
    )
  }

  console.log("All assertions passed.")
})()
