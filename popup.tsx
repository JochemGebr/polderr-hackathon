import { useState } from "react"

function IndexPopup() {
  const [copied, setCopied] = useState(false)
  const fullPageUrl = chrome.runtime.getURL("newtab.html")
  const landlordFeatures = [
    "Landlord likes cleanliness",
    "Stable income preferred",
    "No indoor smoking",
    "Quiet tenant profile",
    "Long-term rent intention"
  ]
  const matchScore = 7
  const llmSuggestion =
    "Hi! I am a tidy and reliable tenant with stable income. I value a quiet home and plan to rent long-term. I treat homes with care and would love to schedule a viewing."

  const copySuggestion = async () => {
    await navigator.clipboard.writeText(llmSuggestion)
    setCopied(true)
    setTimeout(() => setCopied(false), 1500)
  }

  return (
    <div
      style={{
        width: 360,
        padding: 16,
        boxSizing: "border-box",
        fontFamily: "Inter, -apple-system, BlinkMacSystemFont, sans-serif",
        color: "#172033"
      }}>
      <h2 style={{ margin: "0 0 8px", fontSize: 18 }}>Landlord preferences</h2>
      <ul style={{ margin: "0 0 12px", paddingLeft: 18 }}>
        {landlordFeatures.map((feature) => (
          <li key={feature} style={{ marginBottom: 6, fontSize: 14 }}>
            {feature}
          </li>
        ))}
      </ul>

      <div style={{ marginBottom: 12 }}>
        <p style={{ margin: "0 0 6px", fontWeight: 600 }}>Match: {matchScore}/10</p>
        <div
          style={{
            width: "100%",
            height: 8,
            background: "#e7ecf8",
            borderRadius: 999
          }}>
          <div
            style={{
              width: `${matchScore * 10}%`,
              height: "100%",
              background: "#5b84ff",
              borderRadius: 999
            }}
          />
        </div>
      </div>

      <div
        style={{
          background: "#f5f7fb",
          border: "1px solid #dbe3f6",
          borderRadius: 10,
          padding: 10,
          marginBottom: 12
        }}>
        <p style={{ margin: "0 0 8px", fontSize: 13, color: "#4b5874" }}>
          Suggested message:
        </p>
        <p style={{ margin: 0, fontSize: 13, lineHeight: 1.4 }}>{llmSuggestion}</p>
      </div>

      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12 }}>
        <span style={{ fontSize: 13, fontWeight: 600 }}>
          {copied ? "Copied" : "Copy LLM suggestion"}
        </span>
        <button
          onClick={copySuggestion}
          aria-label="Copy LLM suggestion"
          style={{
            border: "1px solid #c8d2ea",
            borderRadius: 8,
            background: "white",
            width: 30,
            height: 30,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            cursor: "pointer"
          }}>
          <svg
            width="14"
            height="14"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden="true">
            <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
          </svg>
        </button>
      </div>

      <div style={{ marginTop: 12 }}>
        <a href={fullPageUrl} target="_blank" rel="noreferrer">
          Open dashboard
        </a>
      </div>
    </div>
  )
}

export default IndexPopup
