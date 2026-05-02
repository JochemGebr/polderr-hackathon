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
  const [error, setError] = useState<string | null>(null)
  
  const [features, setFeatures] = useState<ExtractFeaturesResponse | null>(null)
  const [generatedMessage, setGeneratedMessage] = useState<string | null>(null)
  const [editableMessage, setEditableMessage] = useState<string>("")
  const [copied, setCopied] = useState(false)
  const [pageText, setPageText] = useState<string>("")

  // Determine if we're on Kamernet when popup opens
  useEffect(() => {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      const activeTab = tabs[0]
      if (activeTab?.url && activeTab.url.includes("kamernet.nl")) {
        setIsKamernet(true)
      } else {
        setIsKamernet(false)
      }
    })
  }, [])

  const handleAnalyse = async () => {
    setLoadingState("analysing")
    setError(null)

    try {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true })
      
      if (!tab.id) throw new Error("No active tab")

      // Request text from content script
      // -> Note for integration: Your content script must listen for "GET_PAGE_TEXT" 
      //    and respond with the extracted textual info of the listing.
      const response: { text?: string; error?: string } = await chrome.tabs.sendMessage(tab.id, { 
        action: "GET_PAGE_TEXT" 
      }).catch(err => {
        throw new Error("Could not read page content. Make sure the content script is running.")
      })

      if (response.error || !response.text) {
        throw new Error(response.error || "Could not extract listing information.")
      }

      setPageText(response.text)

      const apiRes = await fetch(`${API_BASE_URL}/extract-listing-features`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ listingText: response.text })
      })

      if (!apiRes.ok) throw new Error("Backend unavailable or returned an error.")

      const data: ExtractFeaturesResponse = await apiRes.json()
      setFeatures(data)
    } catch (err: any) {
      setError(err.message || "An unexpected error occurred.")
    } finally {
      setLoadingState("idle")
    }
  }

  const handleGenerate = async () => {
    if (!features || !pageText) return
    setLoadingState("generating")
    setError(null)

    try {
      const apiRes = await fetch(`${API_BASE_URL}/generate-application-message`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          listingText: pageText,
          motivationPoints: features.recommendedMotivationPoints
        })
      })

      if (!apiRes.ok) throw new Error("Backend unavailable or returned an error.")

      const data: GenerateMessageResponse = await apiRes.json()
      setGeneratedMessage(data.message)
      setEditableMessage(data.message)
    } catch (err: any) {
      setError(err.message || "An unexpected error occurred.")
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
        <h2 className="popup-heading">Open a Kamernet listing</h2>
        <p className="popup-paragraph">
          CrowdApply works when you are viewing a rental listing on Kamernet.
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
        <h2 className="popup-title">CrowdApply</h2>
        <p className="popup-subtitle">Know what to say, know what happened.</p>
      </div>

      {error && (
        <div className="popup-error">
          <p className="popup-error-text">{error}</p>
        </div>
      )}

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
