import { useEffect, useState } from "react"

import { AccountSetupGate } from "./options/components/AccountSetupGate"
import { DashboardContent } from "./options/components/DashboardContent"
import { ProfileModal } from "./options/components/ProfileModal"
import { API_BASE, DEMO_SEED_USER_ID } from "./options/constants"
import {
	AppItem,
	AppStatus,
	FeatureItem,
	SaveStatus,
	SignupStatus,
} from "./options/types"
import { isProfileComplete } from "./options/utils"

function OptionsPage() {
	const [profileName, setProfileName] = useState("")
	const [profileGender, setProfileGender] = useState("")
	const [profileOccupation, setProfileOccupation] = useState("")
	const [profileIncome, setProfileIncome] = useState("")
	const [profileAge, setProfileAge] = useState("")
	const [profileHasPets, setProfileHasPets] = useState(false)
	const [profileSummary, setProfileSummary] = useState("")
	const [userId, setUserId] = useState<string | null>(null)
	const [saveStatus, setSaveStatus] = useState<SaveStatus>("idle")

	const [profileOpen, setProfileOpen] = useState(false)
	const [forceProfileSetup, setForceProfileSetup] = useState(false)

	const [applications, setApplications] = useState<AppItem[]>([])
	const [features, setFeatures] = useState<FeatureItem[]>([])
	const [loading, setLoading] = useState(true)
	const [needsAccountSetup, setNeedsAccountSetup] = useState(false)
	const [acceptingApplicationIds, setAcceptingApplicationIds] = useState<
		Record<string, boolean>
	>({})
	const [acceptStatusMessage, setAcceptStatusMessage] = useState<
		string | null
	>(null)
	const [signupFirstName, setSignupFirstName] = useState("")
	const [signupLastName, setSignupLastName] = useState("")
	const [signupPassword, setSignupPassword] = useState("")
	const [signupRepeatPassword, setSignupRepeatPassword] = useState("")
	const [signupStatus, setSignupStatus] = useState<SignupStatus>("idle")

	useEffect(() => {
		const previousBodyMargin = document.body.style.margin
		document.body.style.margin = "0"
		return () => {
			document.body.style.margin = previousBodyMargin
		}
	}, [])

	async function loadDashboardData(id: string) {
		setLoading(true)
		const [userRes, appsRes, featuresRes] = await Promise.all([
			fetch(`${API_BASE}/users/${id}`),
			fetch(`${API_BASE}/users/${id}/applications`),
			fetch(`${API_BASE}/users/${id}/features`),
		])

		if (userRes.status === 404) {
			chrome.storage.local.remove("userId")
			setUserId(null)
			setNeedsAccountSetup(true)
			setApplications([])
			setFeatures([])
			setLoading(false)
			return
		}

		if (userRes.ok) {
			const user = await userRes.json()
			if (user.name) setProfileName(user.name)
			if (user.gender) setProfileGender(user.gender)
			if (user.occupation) setProfileOccupation(user.occupation)
			if (user.income != null) setProfileIncome(String(user.income))
			if (user.age != null) setProfileAge(String(user.age))
			setProfileHasPets(user.has_pets ?? false)
			if (user.bio) setProfileSummary(user.bio)

			const complete = isProfileComplete({
				name: user.name,
				gender: user.gender,
				occupation: user.occupation,
				income: user.income,
				age: user.age,
				bio: user.bio,
			})
			setForceProfileSetup(!complete)
			setProfileOpen(!complete)
		}
		if (appsRes.ok) setApplications(await appsRes.json())
		else setApplications([])
		if (featuresRes.ok) setFeatures(await featuresRes.json())
		else setFeatures([])
		setNeedsAccountSetup(false)
		setLoading(false)
	}

	useEffect(() => {
		chrome.storage.local.get("userId", (result) => {
			const rawId = result.userId
			const id = typeof rawId === "string" ? rawId.trim() : undefined
			if (
				!id ||
				id === "undefined" ||
				id === "null"
			) {
				chrome.storage.local.remove("userId")
				setNeedsAccountSetup(true)
				setLoading(false)
				return
			}
			setUserId(id)
			void loadDashboardData(id)
		})
	}, [])

	async function createAccount() {
		if (
			!signupFirstName.trim() ||
			!signupLastName.trim() ||
			!signupPassword ||
			!signupRepeatPassword ||
			signupPassword.length !== signupRepeatPassword.length
		) {
			setSignupStatus("error")
			return
		}

		setSignupStatus("creating")
		try {
			chrome.storage.local.set({ userId: DEMO_SEED_USER_ID })
			setUserId(DEMO_SEED_USER_ID)
			setSignupPassword("")
			setSignupRepeatPassword("")
			setSignupStatus("idle")
			await loadDashboardData(DEMO_SEED_USER_ID)
		} catch {
			setSignupStatus("error")
		}
	}

	async function saveProfile() {
		if (
			!isProfileComplete({
				name: profileName,
				gender: profileGender,
				occupation: profileOccupation,
				income: profileIncome,
				age: profileAge,
				bio: profileSummary,
			})
		) {
			setSaveStatus("incomplete")
			return
		}

		setSaveStatus("saving")
		try {
			const body = {
				name: profileName || null,
				gender: profileGender || null,
				occupation: profileOccupation || null,
				income: profileIncome ? parseInt(profileIncome, 10) : null,
				age: profileAge ? parseInt(profileAge, 10) : null,
				has_pets: profileHasPets,
				bio: profileSummary || null,
			}
			if (userId) {
				const res = await fetch(`${API_BASE}/users/${userId}`, {
					method: "PUT",
					headers: { "Content-Type": "application/json" },
					body: JSON.stringify(body),
				})
				if (!res.ok) throw new Error()
			} else {
				const res = await fetch(`${API_BASE}/users`, {
					method: "POST",
					headers: { "Content-Type": "application/json" },
					body: JSON.stringify(body),
				})
				if (!res.ok) throw new Error()
				const created = await res.json()
				const newId = created.user_id as string
				setUserId(newId)
				chrome.storage.local.set({ userId: newId })
			}
			setSaveStatus("saved")
			setForceProfileSetup(false)
			setProfileOpen(false)
			setTimeout(() => setSaveStatus("idle"), 2000)
		} catch {
			setSaveStatus("error")
		}
	}

	async function markApplicationAccepted(applicationId: string) {
		setAcceptStatusMessage(null)
		setAcceptingApplicationIds((prev) => ({
			...prev,
			[applicationId]: true,
		}))

		try {
			const res = await fetch(`${API_BASE}/applications/${applicationId}`, {
				method: "PATCH",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({ status: "ACCEPTED" }),
			})
			if (!res.ok) throw new Error()

			setApplications((prev) =>
				prev.map((app) =>
					app.application_id === applicationId
						? { ...app, status: "ACCEPTED" }
						: app
				)
			)
		} catch {
			setAcceptStatusMessage("Failed to mark application as accepted.")
		} finally {
			setAcceptingApplicationIds((prev) => {
				const next = { ...prev }
				delete next[applicationId]
				return next
			})
		}
	}

	const total = applications.length
	const invited = applications.filter((a) => a.status === "INVITED").length
	const accepted = applications.filter((a) => a.status === "ACCEPTED").length
	const responded = applications.filter((a) => a.status !== "PENDING").length
	const responseRate =
		total > 0 ? Math.round((responded / total) * 100) : 0

	const statusCounts = (
		["PENDING", "INVITED", "REJECTED", "GHOSTED", "ACCEPTED"] as const
	)
		.map((status) => ({
			status,
			count: applications.filter((app) => app.status === status).length,
		}))
		.filter((entry) => entry.count > 0) as {
		status: AppStatus
		count: number
	}[]

	if (needsAccountSetup) {
		return (
			<AccountSetupGate
				signupFirstName={signupFirstName}
				signupLastName={signupLastName}
				signupPassword={signupPassword}
				signupRepeatPassword={signupRepeatPassword}
				signupStatus={signupStatus}
				setSignupFirstName={setSignupFirstName}
				setSignupLastName={setSignupLastName}
				setSignupPassword={setSignupPassword}
				setSignupRepeatPassword={setSignupRepeatPassword}
				onCreateAccount={createAccount}
			/>
		)
	}

	return (
		<>
			<DashboardContent
				loading={loading}
				applications={applications}
				features={features}
				total={total}
				invited={invited}
				accepted={accepted}
				responded={responded}
				responseRate={responseRate}
				statusCounts={statusCounts}
				onOpenProfile={() => setProfileOpen(true)}
				onMarkAccepted={markApplicationAccepted}
				acceptingApplicationIds={acceptingApplicationIds}
				acceptStatusMessage={acceptStatusMessage}
			/>
			<ProfileModal
				profileOpen={profileOpen}
				forceProfileSetup={forceProfileSetup}
				profileName={profileName}
				profileOccupation={profileOccupation}
				profileIncome={profileIncome}
				profileGender={profileGender}
				profileAge={profileAge}
				profileHasPets={profileHasPets}
				profileSummary={profileSummary}
				saveStatus={saveStatus}
				setProfileName={setProfileName}
				setProfileOccupation={setProfileOccupation}
				setProfileIncome={setProfileIncome}
				setProfileGender={setProfileGender}
				setProfileAge={setProfileAge}
				setProfileHasPets={setProfileHasPets}
				setProfileSummary={setProfileSummary}
				onClose={() => setProfileOpen(false)}
				onSave={saveProfile}
			/>
		</>
	)
}

export default OptionsPage
