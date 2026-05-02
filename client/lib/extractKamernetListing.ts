export interface ExtractedKamernetListing {
  title: string
  text: string
  url: string
  price: number | null
  location: string | null
  listing_type: string | null
  
}

export const extractKamernetListingFromTab = async (
  tabId: number
): Promise<ExtractedKamernetListing> => {
  const [result] = await chrome.scripting.executeScript({
    target: { tabId },
    func: () => {
      const cleanText = (text: string | null | undefined) =>
        text?.replace(/\s+/g, " ").trim() ?? ""

      const getText = (selector: string) => {
        const element = document.querySelector<HTMLElement>(selector)
        return cleanText(element?.innerText)
      }

      const parsePrice = (priceText: string | null) => {
        if (!priceText) return null

        const match = priceText.match(/€?\s*([\d.,]+)/)
        if (!match) return null

        const normalised = match[1].replace(/\./g, "").replace(",", ".")
        const parsed = Number(normalised)

        return Number.isFinite(parsed) ? parsed : null
      }

const getLocation = () => {
  const locationDiv =
    document.querySelector<HTMLElement>("div[class^='Header_locationDetails_']") ??
    document.querySelector<HTMLElement>("div[class*=' Header_locationDetails_']")

  const locationFromDiv = cleanText(locationDiv?.innerText)

  if (locationFromDiv) {
    return locationFromDiv
  }

  const anchors = Array.from(document.querySelectorAll<HTMLAnchorElement>("a"))

  const locationAnchor = anchors.find((anchor) => {
    const text = cleanText(anchor.innerText)
    const href = anchor.href

    return (
      text.length > 0 &&
      href.includes("/huren/") &&
      !href.includes("kamer-")
    )
  })

  return cleanText(locationAnchor?.innerText) || null
}

      const getListingType = (url: string) => {
        try {
          const parsedUrl = new URL(url)
          const parts = parsedUrl.pathname.split("/").filter(Boolean)

          // Example:
          // /huren/amsterdam/kamer/kamer-123456
          return parts[2] ?? null
        } catch {
          return null
        }
      }

      const url = window.location.href

      const title =
        getText("h3") ||
        cleanText(document.title) ||
        "Kamernet listing"

        const getDescription = () => {
        const aboutPreText =
            document.querySelector<HTMLElement>("[class^='About_preText_']") ??
            document.querySelector<HTMLElement>("[class*=' About_preText_']")

        const descriptionParagraph = aboutPreText?.querySelector<HTMLElement>("p")

        return cleanText(descriptionParagraph?.innerText) || ""
        }

        const getPrice = () => {
        const firstRentalCostRow =
            document.querySelector<HTMLElement>("[class^='RentalCosts_cardRow_']") ??
            document.querySelector<HTMLElement>("[class*=' RentalCosts_cardRow_']")

        const priceText = cleanText(
            firstRentalCostRow?.querySelector<HTMLElement>("h6")?.innerText
        )

        if (!priceText) return null

        const match = priceText.match(/€?\s*([\d.,]+)/)
        if (!match) return null

        const normalised = match[1].replace(/\./g, "").replace(",", ".")
        const parsed = Number(normalised)

        return Number.isFinite(parsed) ? parsed : null
        }

      const fallbackText = cleanText(document.body.innerText)

      return {
        title,
        text: getDescription(),
        url,
        price: getPrice(),
        location: getLocation(),
      }
    }
  })

  const extracted = result.result

  if (!extracted?.text) {
    throw new Error("Could not extract listing information from the page DOM.")
  }

  return extracted
}