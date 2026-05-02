import { extractLandlordFeatures } from "./extract-landlord-features"

const apiKey = process.env.GOOGLE_AI_API_KEY
if (!apiKey) throw new Error("Set GOOGLE_AI_API_KEY env var")

const sampleText = process.argv[2] ?? `
  No pets, prefer cleanliness. only women allowed.
`

;(async () => {
  const features = await extractLandlordFeatures(sampleText, apiKey)
  console.log("Extracted landlord features:", features)
})()
