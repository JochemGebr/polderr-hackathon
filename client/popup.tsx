import { useEffect, useState } from "react"
import "./popup.css"

const API_BASE_URL = "http://localhost:8000"

interface ExtractFeaturesResponse {
  estimatedFitScore: number
  listingFeatures: string[]
  recommendedMotivationPoints: string[]
}

interface GenerateMessageResponse {
  message: string
}

function IndexPopup() {
  const [isKamernet, setIsKamernet] = useState<boolean | null>(null)
  const [loadingState, setLoadingState] = useState<"idle" | "analysing" | "generating">("idle")
  
  
  const [features, setFeatures] = useState<ExtractFeaturesResponse | null>(null)
  const [generatedMessage, setGeneratedMessage] = useState<string | null>(null)
  const [editableMessage, setEditableMessage] = useState<string>("")
  const [copied, setCopied] = useState(false)
  const [pageText, setPageText] = useState<string>("")
  const fullPageUrl = chrome.runtime.getURL("options.html")

  // Determine if we're on Kamernet when popup opens
  useEffect(() => {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      const activeTab = tabs[0]
      const url = activeTab?.url

      if (!url) {
        setIsKamernet(false)
        return
      }

      try {
        const parsedUrl = new URL(url)
        const isKamernetHost = parsedUrl.hostname.endsWith("kamernet.nl")
        const isListingPath = /^\/huren\/[^/]+\/[^/]+\/kamer-\d+/.test(parsedUrl.pathname)
        setIsKamernet(isKamernetHost && isListingPath)
      } catch {
        setIsKamernet(false)
      }
    })
  }, [])

  const handleAnalyse = async () => {
    setLoadingState("analysing")

    try {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true })

      const response: any = await chrome.tabs.sendMessage(tab!.id!, { action: "GET_PAGE_TEXT" })

      setPageText(response?.text || "")

      const apiRes = await fetch(`${API_BASE_URL}/extract-listing-features`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ listingText: response?.text || "" })
      })

      const data: ExtractFeaturesResponse = await apiRes.json()
      setFeatures(data)
    } finally {
      setLoadingState("idle")
    }
  }

  const handleGenerate = async () => {
    if (!features || !pageText) return
    setLoadingState("generating")

    try {
      const apiRes = await fetch(`${API_BASE_URL}/generate-application-message`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          listingText: pageText,
          motivationPoints: features.recommendedMotivationPoints
        })
      })

      const data: GenerateMessageResponse = await apiRes.json()
      setGeneratedMessage(data.message)
      setEditableMessage(data.message)
    } finally {
      setLoadingState("idle")
    }
  }

  const copySuggestion = async () => {
    await navigator.clipboard.writeText(editableMessage)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  if (isKamernet === null) {
    return <div className="popup-container">Loading...</div>
  }

  if (!isKamernet) {
    return (
      <div className="popup-container">
        <div className="popup-heading-row">
          <h2 className="popup-heading">No listing found</h2>
          <button
            className="popup-icon-button"
            onClick={() => chrome.tabs.create({ url: fullPageUrl })}
            aria-label="Open full dashboard"
            title="Open full dashboard"
          >
            <svg
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              aria-hidden="true"
            >
              <path d="M20 21a8 8 0 1 0-16 0" />
              <circle cx="12" cy="7" r="4" />
            </svg>
          </button>
        </div>
        <p className="popup-paragraph">
          Please go to a Kamernet listing to use CrowdApply.
        </p>
        <button className="popup-button popup-button-disabled" disabled>
          Analyse listing
        </button>
      </div>
    )
  }

  return (
    <div className="popup-container">
      <div className="popup-header">
        <div>
          <h2 className="popup-title">CrowdApply</h2>
          <p className="popup-subtitle">Know what to say, know what happened.</p>
        </div>
        <button
          className="popup-icon-button"
          onClick={() => chrome.tabs.create({ url: fullPageUrl })}
          aria-label="Open full dashboard"
          title="Open full dashboard"
        >
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden="true"
          >
            <path d="M20 21a8 8 0 1 0-16 0" />
            <circle cx="12" cy="7" r="4" />
          </svg>
        </button>
      </div>

      

      {!features && (
        <button 
          className="popup-button popup-button-primary"
          onClick={handleAnalyse}
          disabled={loadingState === "analysing"}
        >
          {loadingState === "analysing" ? "Analysing listing..." : "Analyse listing"}
        </button>
      )}

      {features && !generatedMessage && (
        <div className="popup-card">
          <div className="popup-section">
            <p className="popup-score">
              Estimated fit score: {features.estimatedFitScore}%
            </p>
            <p className="popup-disclaimer">
              *This is an estimate based on previous application patterns. It does not guarantee acceptance.
            </p>
            <div className="popup-progress">
              <div className="popup-progress-fill" style={{ width: `${features.estimatedFitScore}%` }} />
            </div>
          </div>

          <div className="popup-section">
            <p className="popup-section-title">Detected Features:</p>
            <div className="popup-badges">
              {features.listingFeatures.map((f, i) => (
                <span key={i} className="popup-badge">{f}</span>
              ))}
            </div>
          </div>

          <div className="popup-section">
            <p className="popup-section-title">Top Motivation Points:</p>
            <ul className="popup-list">
              {features.recommendedMotivationPoints.map((point, i) => (
                <li key={i} className="popup-list-item">{point}</li>
              ))}
            </ul>
          </div>

          <button 
            className="popup-button popup-button-primary"
            onClick={handleGenerate}
            disabled={loadingState === "generating"}
          >
            {loadingState === "generating" ? "Writing personalised message..." : "Generate message"}
          </button>
        </div>
      )}

      {generatedMessage && (
        <div className="popup-card">
          <p className="popup-message-title">Message Draft</p>
          <p className="popup-message-hint">
            Make sure to review and edit before sending!
          </p>
          <textarea
            className="popup-textarea"
            value={editableMessage}
            onChange={(e) => setEditableMessage(e.target.value)}
            rows={8}
          />
          <div className="popup-action-row">
            <button className="popup-button popup-button-secondary" onClick={copySuggestion}>
              {copied ? "Copied!" : "Copy message"}
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
export default IndexPopup
