import { useEffect, useState } from "react"
import "./popup.css"
import { extractKamernetListingFromTab } from "./lib/extractKamernetListing"

const API_BASE_URL = "http://localhost:3001"

interface ExtractedFeature {
  feature_id: string
  name: string
  description?: string | null
  score: number
}

interface ListingResponse {
  listing_id: string
  features: ExtractedFeature[]
}

interface UserResponse {
  user_id: string
}

interface AnalysisResult {
  listingId: string
  userId: string
  features: ExtractedFeature[]
}

interface RecommendationResponse {
  message: string
  key_strengths: string[]
  addressed_concerns: string[]
}

function IndexPopup() {
  const [isKamernet, setIsKamernet] = useState<boolean | null>(null)
  const [loadingState, setLoadingState] = useState<"idle" | "analysing" | "generating">("idle")
  
  
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null)
  const [recommendation, setRecommendation] = useState<RecommendationResponse | null>(null)
  const [editableMessage, setEditableMessage] = useState<string>("")
  const [copied, setCopied] = useState(false)
  const [pageText, setPageText] = useState<string>("")
  const fullPageUrl = chrome.runtime.getURL("options.html")

  const apiFetch = async <T,>(path: string, options?: RequestInit): Promise<T> => {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...(options?.headers ?? {})
      }
    })

    if (!response.ok) {
      const errorText = await response.text()
      throw new Error(errorText || "Backend unavailable or returned an error.")
    }

    return response.json() as Promise<T>
  }

  const buildExternalId = (url: string | undefined) => {
    if (!url) return `kamernet-${Date.now()}`
    const match = url.match(/kamer-(\d+)/)
    if (match) return `kamernet-${match[1]}`
    const sanitized = url.replace(/[^a-zA-Z0-9_-]/g, "_").slice(-60)
    return `kamernet-${sanitized}`
  }

  const getOrCreateUserId = async () => {
    const storedId = localStorage.getItem("crowdapplyUserId")
    if (storedId) return storedId

    const user = await apiFetch<UserResponse>("/api/users", {
      method: "POST",
      body: JSON.stringify({
        name: "Extension User",
        occupation: "",
        income: null,
        age: null,
        has_pets: false,
        bio: "",
        profile: { source: "browser-extension" }
      })
    })

    localStorage.setItem("crowdapplyUserId", user.user_id)
    return user.user_id
  }

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
        const isNlListingPath = /^\/huren\/[^/]+\/[^/]+\/kamer-\d+/.test(
          parsedUrl.pathname
        )
        const isEnListingPath = /^\/en\/for-rent\/[^/]+\/[^/]+\/[^/]+/.test(
          parsedUrl.pathname
        )
        setIsKamernet(isKamernetHost && (isNlListingPath || isEnListingPath))
      } catch {
        setIsKamernet(false)
      }
    })
  }, [])

  const handleAnalyse = async () => {
    setLoadingState("analysing")

    try {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true })

      if (!tab.id) throw new Error("No active tab")

      const extracted = await extractKamernetListingFromTab(tab.id)

      setPageText(extracted.text)
      console.log(extracted)
      console.log(buildExternalId(tab.url))

      const userId = await getOrCreateUserId()

      const listing = await apiFetch<ListingResponse>("/api/listings", {
        method: "POST",
        body: JSON.stringify({
          external_id: buildExternalId(tab.url),
          url: extracted.url,
          title: extracted.title,
          description: extracted.text,
          price: extracted.price,
          location: extracted.location,
          details: extracted.details,
          ideal_tenant: extracted.idealTenant,
          accepted_person_id: null
        })
      })

      setAnalysis({
        listingId: listing.listing_id,
        userId,
        features: listing.features
      })

      setRecommendation(null)
      setEditableMessage("")
    } catch (err: any) {
      console.error(err)
    } finally {
      setLoadingState("idle")
    }
  }

  const handleGenerate = async () => {
    if (!analysis || !pageText) return
    setLoadingState("generating")

    try {
      const data = await apiFetch<RecommendationResponse>(
        `/api/recommendations?listing_id=${analysis.listingId}&user_id=${analysis.userId}`
      )
      setRecommendation(data)
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


      {!analysis && (
        <button 
          className="popup-button popup-button-primary"
          onClick={handleAnalyse}
          disabled={loadingState === "analysing"}
        >
          {loadingState === "analysing" ? "Analysing listing..." : "Analyse listing"}
        </button>
      )}

      {analysis && !recommendation && (
        <div className="popup-card">
          <div className="popup-section">
            <p className="popup-section-title">Detected features</p>
            {analysis.features.length > 0 ? (
              <div className="popup-badges">
                {analysis.features.map((feature) => (
                  <span key={feature.feature_id} className="popup-badge">
                    {feature.name}
                  </span>
                ))}
              </div>
            ) : (
              <p className="popup-disclaimer">No features detected yet.</p>
            )}
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

      {recommendation && (
        <div className="popup-card">
          <p className="popup-message-title">Message Draft</p>
          <p className="popup-message-hint">
            Make sure to review and edit before sending!
          </p>
          <div className="popup-section">
            <p className="popup-section-title">Key strengths</p>
            <div className="popup-badges">
              {recommendation.key_strengths.map((strength, i) => (
                <span key={i} className="popup-badge">{strength}</span>
              ))}
            </div>
          </div>
          {recommendation.addressed_concerns.length > 0 ? (
            <div className="popup-section">
              <p className="popup-section-title">Concerns addressed</p>
              <ul className="popup-list">
                {recommendation.addressed_concerns.map((concern, i) => (
                  <li key={i} className="popup-list-item">{concern}</li>
                ))}
              </ul>
            </div>
          ) : null}
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
