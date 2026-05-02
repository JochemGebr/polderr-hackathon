import { useEffect, useState } from "react"
import "./popup.css"
import { extractKamernetListingFromTab } from "./lib/extractKamernetListing"

const API_BASE_URL = "http://localhost:3001"

interface MatchFeature {
  name: string
  pretty_name: string
  score: number
}

interface ListingResponse {
  listing_id: string
  match_score: number
  features: MatchFeature[]
}

interface UserResponse {
  user_id: string
}

interface AnalysisResult {
  listingId: string
  userId: string
  matchScore: number
  features: MatchFeature[]
}

interface RecommendationResponse {
  message: string
}

function IndexPopup() {
  const [isKamernet, setIsKamernet] = useState<boolean | null>(null)
  const [loadingState, setLoadingState] = useState<"idle" | "analysing" | "generating">("idle")
  const [error, setError] = useState<string | null>(null)  
  
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
    if (!url) return `${Date.now()}`
    const match = url.match(/(\d+)(?:\/)?$/)
    if (match) return match[1]
    const sanitized = url.replace(/[^a-zA-Z0-9_-]/g, "_").slice(-60)
    return sanitized
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

      const userId = "00000000-0000-0000-0000-000000000001"

      const listing = await apiFetch<ListingResponse>("/api/listings", {
        method: "POST",
        body: JSON.stringify({
          user_id: userId,
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
        matchScore: listing.match_score,
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
    if (!analysis) return

    setError(null)
    setLoadingState("generating")

    try {
      const data = await apiFetch<RecommendationResponse>(
        `/api/recommendations?listing_id=${encodeURIComponent(
          analysis.listingId
        )}&user_id=${encodeURIComponent(analysis.userId)}`,
        {
          method: "POST"
        }
      )

      setRecommendation({
        message: data.message
      })

      setEditableMessage(data.message)
    } catch (err: any) {
      console.error(err)
      setError(err.message || "Could not generate the message.")
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
          <p className="popup-subtitle">know what to say, know what happened.</p>
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
          <div className="popup-impact-card">
            <div className="popup-impact-header">
              <p className="popup-impact-title">What correlates with acceptance</p>
              <p className="popup-impact-score">
                Match score: {Math.round(analysis.matchScore * 100)}%
              </p>
            </div>
            <div className="popup-impact-list">
              {analysis.features.map((feature) => {
                const percent = Math.round(Math.abs(feature.score) * 100)
                const isPositive = feature.score >= 0
                return (
                  <div key={feature.name} className="popup-impact-row">
                    <span className="popup-impact-label">{feature.pretty_name}</span>
                    <div className="popup-impact-bar">
                      <div
                        className={
                          isPositive
                            ? "popup-impact-fill popup-impact-fill--positive"
                            : "popup-impact-fill popup-impact-fill--negative"
                        }
                        style={{ width: `${percent}%` }}
                      />
                    </div>
                    <span
                      className={
                        isPositive
                          ? "popup-impact-value popup-impact-value--positive"
                          : "popup-impact-value popup-impact-value--negative"
                      }
                    >
                      {isPositive ? "+" : "-"}
                      {percent}%
                    </span>
                  </div>
                )
              })}
            </div>
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
          <textarea
            className="popup-textarea"
            value={editableMessage}
            onChange={(e) => setEditableMessage(e.target.value)}
            rows={8}
          />
          <div className="popup-action-row">
            <button className="popup-button popup-button-primary" onClick={copySuggestion}>
              {copied ? "Copied!" : "Copy message"}
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
export default IndexPopup
