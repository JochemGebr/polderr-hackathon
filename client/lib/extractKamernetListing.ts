export interface ExtractedKamernetListing {
  title: string
  text: string
  url: string
  price: number | null
  location: string | null
  details: string | null
  idealTenant: string | null
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

    return cleanText(locationDiv?.innerText) || null
    }

    const getDetails = () => {
        const detailsRoot =
            document.querySelector<HTMLElement>("[class^='Details_root_']") ??
            document.querySelector<HTMLElement>("[class*=' Details_root_']")

        return cleanText(detailsRoot?.innerText) || null
        }

    const getIdeal = () => {
        const idealTenantRoot =
            document.querySelector<HTMLElement>("[class^='IdealTenant_root_']") ??
            document.querySelector<HTMLElement>("[class*=' IdealTenant_root_']")

        return cleanText(idealTenantRoot?.innerText) || null
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
        details: getDetails(),
        idealTenant: getIdeal()
      }
    }
  })

  const extracted = result.result

  if (!extracted?.text) {
    throw new Error("Could not extract listing information from the page DOM.")
  }

  return extracted
}