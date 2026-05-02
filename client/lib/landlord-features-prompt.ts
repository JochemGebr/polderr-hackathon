export function buildPrompt(text: string, existingKeys: string[]): string {
  const existingKeysSection =
    existingKeys.length > 0
      ? `\nPrefer reusing these existing keys over inventing synonyms:\n` +
        `${existingKeys.join(", ")}\n`
      : ""

  return `You are analyzing a rental applicant's text to identify traits
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
}
