import { useEffect, useState } from "react"
import {
	Bar,
	BarChart,
	Cell,
	ResponsiveContainer,
	Tooltip,
	XAxis,
	YAxis,
} from "recharts"

const API_BASE = "http://localhost:3001/api"

type AppStatus =
	| "PENDING"
	| "INVITED"
	| "REJECTED"
	| "GHOSTED"
	| "ACCEPTED"

interface AppItem {
	application_id: string
	status: AppStatus
	applied_at: string
	listing: {
		listing_id: string
		title: string
		location: string | null
		price: number | null
		listing_type: string | null
	}
	compatibility: number | null
}

interface FeatureItem {
	name: string
	score: number
}

const STATUS_COLOR: Record<AppStatus, string> = {
	PENDING: "#a0aec0",
	INVITED: "#5b84ff",
	REJECTED: "#e05252",
	GHOSTED: "#718096",
	ACCEPTED: "#20a67a",
}

function StatusBadge({ status }: { status: AppStatus }) {
	return (
		<span
			style={{
				display: "inline-block",
				padding: "2px 10px",
				borderRadius: 20,
				fontSize: 11,
				fontWeight: 700,
				letterSpacing: "0.04em",
				background: STATUS_COLOR[status] + "22",
				color: STATUS_COLOR[status],
			}}>
			{status}
		</span>
	)
}

function formatPrice(cents: number | null) {
	if (cents == null) return null
	return `€${Math.round(cents / 100)}/mo`
}

function formatDate(iso: string) {
	return new Date(iso).toLocaleDateString("en-GB", {
		day: "numeric",
		month: "short",
	})
}

function OptionsPage() {
	const [isProfileOpen, setIsProfileOpen] = useState(false)
	const [profileName, setProfileName] = useState("")
	const [profileGender, setProfileGender] = useState("")
	const [profileOccupation, setProfileOccupation] = useState("")
	const [profileIncome, setProfileIncome] = useState("")
	const [profileAge, setProfileAge] = useState("")
	const [profileHasPets, setProfileHasPets] = useState(false)
	const [profileSummary, setProfileSummary] = useState("")
	const [userId, setUserId] = useState<string | null>(null)
	const [saveStatus, setSaveStatus] = useState<
		"idle" | "saving" | "saved" | "error"
	>("idle")

	const [applications, setApplications] = useState<AppItem[]>([])
	const [features, setFeatures] = useState<FeatureItem[]>([])
	const [loading, setLoading] = useState(true)

	useEffect(() => {
		chrome.storage.local.get("userId", async (result) => {
			const id = result.userId as string | undefined
			if (!id) {
				setLoading(false)
				return
			}
			setUserId(id)

			const [userRes, appsRes, featuresRes] = await Promise.all([
				fetch(`${API_BASE}/users/${id}`),
				fetch(`${API_BASE}/users/${id}/applications`),
				fetch(`${API_BASE}/users/${id}/features`),
			])

			if (userRes.ok) {
				const user = await userRes.json()
				if (user.name) setProfileName(user.name)
				if (user.gender) setProfileGender(user.gender)
				if (user.occupation) setProfileOccupation(user.occupation)
				if (user.income != null)
					setProfileIncome(String(user.income))
				if (user.age != null) setProfileAge(String(user.age))
				setProfileHasPets(user.has_pets ?? false)
				if (user.bio) setProfileSummary(user.bio)
			}
			if (appsRes.ok) setApplications(await appsRes.json())
			if (featuresRes.ok) setFeatures(await featuresRes.json())
			setLoading(false)
		})
	}, [])

	async function saveProfile() {
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
			setTimeout(() => setSaveStatus("idle"), 2000)
		} catch {
			setSaveStatus("error")
		}
	}

	const total = applications.length
	const invited = applications.filter(
		(a) => a.status === "INVITED"
	).length
	const accepted = applications.filter(
		(a) => a.status === "ACCEPTED"
	).length
	const responded = applications.filter(
		(a) => a.status !== "PENDING"
	).length
	const responseRate =
		total > 0 ? Math.round((responded / total) * 100) : 0

	const statusCounts = (
		["PENDING", "INVITED", "REJECTED", "GHOSTED", "ACCEPTED"] as const
	)
		.map((s) => ({
			status: s,
			count: applications.filter((a) => a.status === s).length,
		}))
		.filter((d) => d.count > 0)

	const inputStyle: React.CSSProperties = {
		width: "100%",
		border: "1px solid #c8d2ea",
		borderRadius: 8,
		padding: "8px 10px",
		boxSizing: "border-box",
		fontSize: 13,
	}

	return (
		<main
			style={{
				minHeight: "100vh",
				padding: 24,
				boxSizing: "border-box",
				background: "#f5f7fb",
				color: "#172033",
				fontFamily:
					"Montserrat, -apple-system, BlinkMacSystemFont, sans-serif",
			}}>
			<div style={{ maxWidth: 1200, margin: "0 auto" }}>
				{/* Header */}
				<header
					style={{
						display: "flex",
						justifyContent: "space-between",
						alignItems: "center",
						marginBottom: 20,
					}}>
					<div>
						<h1 style={{ margin: 0 }}>Dashboard</h1>
						<p style={{ margin: "4px 0 0", color: "#4b5874" }}>
							Track your rental applications at a glance
						</p>
					</div>
					<button
						onClick={() => setIsProfileOpen((v) => !v)}
						style={{
							border: "1px solid #c8d2ea",
							borderRadius: 10,
							background: "white",
							padding: "10px 14px",
							cursor: "pointer",
							fontWeight: 600,
						}}>
						{isProfileOpen ? "Close profile" : "Profile"}
					</button>
				</header>

				{/* Stats */}
				<section
					style={{
						display: "grid",
						gridTemplateColumns: "repeat(4, minmax(0, 1fr))",
						gap: 12,
						marginBottom: 20,
					}}>
					{[
						["Applications sent", String(total), "total"],
						[
							"Interview invites",
							String(invited),
							total > 0
								? `${Math.round((invited / total) * 100)}% conversion`
								: "—",
						],
						[
							"Response rate",
							`${responseRate}%`,
							`${responded} of ${total} replied`,
						],
						["Accepted", String(accepted), "offers received"],
					].map(([title, value, subtitle]) => (
						<article
							key={title}
							style={{
								background: "white",
								borderRadius: 12,
								padding: 14,
								border: "1px solid #e5ebf8",
							}}>
							<h2
								style={{
									margin: 0,
									fontSize: 13,
									color: "#4b5874",
									fontWeight: 500,
								}}>
								{title}
							</h2>
							<p
								style={{
									margin: "8px 0 4px",
									fontSize: 28,
									fontWeight: 700,
								}}>
								{loading ? "—" : value}
							</p>
							<p
								style={{
									margin: 0,
									fontSize: 12,
									color: "#4b5874",
								}}>
								{subtitle}
							</p>
						</article>
					))}
				</section>

				{/* Main content */}
				<div
					style={{
						display: "grid",
						gridTemplateColumns: "1fr 320px",
						gap: 12,
						alignItems: "start",
					}}>
					{/* Applications list */}
					<article
						style={{
							background: "white",
							borderRadius: 12,
							border: "1px solid #e5ebf8",
							padding: 16,
						}}>
						<h2 style={{ margin: "0 0 14px", fontSize: 16 }}>
							Applications
						</h2>

						{loading ? (
							<p style={{ color: "#4b5874", fontSize: 13 }}>
								Loading…
							</p>
						) : applications.length === 0 ? (
							<p style={{ color: "#4b5874", fontSize: 13 }}>
								No applications yet. Apply to listings and they
								will appear here.
							</p>
						) : (
							<div
								style={{
									display: "flex",
									flexDirection: "column",
									gap: 10,
								}}>
								{applications.map((app) => (
									<div
										key={app.application_id}
										style={{
											padding: "10px 12px",
											borderRadius: 8,
											border: "1px solid #e5ebf8",
											display: "grid",
											gridTemplateColumns: "1fr auto",
											gap: "4px 12px",
											alignItems: "start",
										}}>
										<div>
											<p
												style={{
													margin: 0,
													fontWeight: 600,
													fontSize: 14,
												}}>
												{app.listing.title}
											</p>
											<p
												style={{
													margin: "2px 0 0",
													fontSize: 12,
													color: "#4b5874",
												}}>
												{[
													app.listing.location,
													formatPrice(app.listing.price),
													app.listing.listing_type,
												]
													.filter(Boolean)
													.join(" · ")}
											</p>
										</div>
										<StatusBadge status={app.status} />

										<p
											style={{
												margin: 0,
												fontSize: 12,
												color: "#4b5874",
											}}>
											Applied {formatDate(app.applied_at)}
										</p>
										{app.compatibility != null && (
											<div
												style={{
													display: "flex",
													alignItems: "center",
													gap: 6,
													justifyContent: "flex-end",
												}}>
												<div
													style={{
														width: 60,
														height: 4,
														borderRadius: 2,
														background: "#e5ebf8",
														overflow: "hidden",
													}}>
													<div
														style={{
															width: `${app.compatibility * 100}%`,
															height: "100%",
															background: "#5b84ff",
															borderRadius: 2,
														}}
													/>
												</div>
												<span
													style={{
														fontSize: 11,
														color: "#4b5874",
														whiteSpace: "nowrap",
													}}>
													{Math.round(
														app.compatibility * 100
													)}
													% match
												</span>
											</div>
										)}
									</div>
								))}
							</div>
						)}
					</article>

					{/* Right sidebar */}
					<div
						style={{
							display: "flex",
							flexDirection: "column",
							gap: 12,
						}}>
						{/* Status breakdown chart */}
						{!loading && statusCounts.length > 0 && (
							<article
								style={{
									background: "white",
									borderRadius: 12,
									border: "1px solid #e5ebf8",
									padding: 16,
								}}>
								<h2
									style={{
										margin: "0 0 12px",
										fontSize: 14,
									}}>
									By status
								</h2>
								<ResponsiveContainer width="100%" height={160}>
									<BarChart
										data={statusCounts}
										margin={{
											top: 0,
											right: 0,
											bottom: 0,
											left: -20,
										}}>
										<XAxis
											dataKey="status"
											tick={{ fontSize: 10 }}
											tickLine={false}
											axisLine={false}
										/>
										<YAxis
											allowDecimals={false}
											tick={{ fontSize: 10 }}
											tickLine={false}
											axisLine={false}
										/>
										<Tooltip
											cursor={{ fill: "#f5f7fb" }}
											contentStyle={{
												fontSize: 12,
												borderRadius: 8,
												border: "1px solid #e5ebf8",
											}}
										/>
										<Bar dataKey="count" radius={[4, 4, 0, 0]}>
											{statusCounts.map((entry) => (
												<Cell
													key={entry.status}
													fill={STATUS_COLOR[entry.status as AppStatus]}
												/>
											))}
										</Bar>
									</BarChart>
								</ResponsiveContainer>
							</article>
						)}

						{/* Profile signals */}
						{!loading && features.length > 0 && (
							<article
								style={{
									background: "white",
									borderRadius: 12,
									border: "1px solid #e5ebf8",
									padding: 16,
								}}>
								<h2
									style={{
										margin: "0 0 12px",
										fontSize: 14,
									}}>
									Your profile signals
								</h2>
								<div
									style={{
										display: "flex",
										flexDirection: "column",
										gap: 8,
									}}>
									{features
										.slice()
										.sort((a, b) => b.score - a.score)
										.map((f) => (
											<div key={f.name}>
												<div
													style={{
														display: "flex",
														justifyContent:
															"space-between",
														fontSize: 12,
														marginBottom: 3,
													}}>
													<span>
														{f.name.replace(/_/g, " ")}
													</span>
													<span style={{ color: "#4b5874" }}>
														{Math.round(f.score * 100)}%
													</span>
												</div>
												<div
													style={{
														height: 4,
														borderRadius: 2,
														background: "#e5ebf8",
														overflow: "hidden",
													}}>
													<div
														style={{
															width: `${f.score * 100}%`,
															height: "100%",
															background: "#5b84ff",
															borderRadius: 2,
														}}
													/>
												</div>
											</div>
										))}
								</div>
							</article>
						)}
					</div>
				</div>
			</div>

			{/* Profile modal */}
			{isProfileOpen && (
				<div
					style={{
						position: "fixed",
						inset: 0,
						background: "rgba(10, 18, 38, 0.45)",
						display: "flex",
						alignItems: "center",
						justifyContent: "center",
						padding: 16,
					}}>
					<aside
						style={{
							width: "100%",
							maxWidth: 540,
							background: "white",
							borderRadius: 12,
							border: "1px solid #e5ebf8",
							padding: 16,
							boxSizing: "border-box",
							maxHeight: "85vh",
							overflowY: "auto",
						}}>
						<div
							style={{
								display: "flex",
								justifyContent: "space-between",
								alignItems: "center",
								marginBottom: 12,
							}}>
							<h2 style={{ margin: 0, fontSize: 16 }}>Profile</h2>
							<button
								onClick={() => setIsProfileOpen(false)}
								style={{
									border: "1px solid #c8d2ea",
									borderRadius: 8,
									background: "white",
									padding: "6px 10px",
									cursor: "pointer",
								}}>
								Close
							</button>
						</div>

						<label
							style={{
								display: "block",
								marginBottom: 6,
								fontSize: 13,
							}}>
							Name
						</label>
						<input
							value={profileName}
							onChange={(e) => setProfileName(e.target.value)}
							style={{ ...inputStyle, marginBottom: 12 }}
						/>

						<div
							style={{
								display: "grid",
								gridTemplateColumns: "1fr 1fr",
								gap: 12,
								marginBottom: 12,
							}}>
							<div>
								<label
									style={{
										display: "block",
										marginBottom: 6,
										fontSize: 13,
									}}>
									Gender
								</label>
								<input
									value={profileGender}
									onChange={(e) =>
										setProfileGender(e.target.value)
									}
									style={inputStyle}
								/>
							</div>
							<div>
								<label
									style={{
										display: "block",
										marginBottom: 6,
										fontSize: 13,
									}}>
									Age
								</label>
								<input
									type="number"
									value={profileAge}
									onChange={(e) =>
										setProfileAge(e.target.value)
									}
									style={inputStyle}
								/>
							</div>
						</div>

						<label
							style={{
								display: "block",
								marginBottom: 6,
								fontSize: 13,
							}}>
							Occupation
						</label>
						<input
							value={profileOccupation}
							onChange={(e) =>
								setProfileOccupation(e.target.value)
							}
							style={{ ...inputStyle, marginBottom: 12 }}
						/>

						<label
							style={{
								display: "block",
								marginBottom: 6,
								fontSize: 13,
							}}>
							Monthly income (€)
						</label>
						<input
							type="number"
							value={profileIncome}
							onChange={(e) => setProfileIncome(e.target.value)}
							style={{ ...inputStyle, marginBottom: 12 }}
						/>

						<label
							style={{
								display: "flex",
								alignItems: "center",
								gap: 8,
								marginBottom: 12,
								fontSize: 13,
								cursor: "pointer",
							}}>
							<input
								type="checkbox"
								checked={profileHasPets}
								onChange={(e) =>
									setProfileHasPets(e.target.checked)
								}
							/>
							Has pets
						</label>

						<label
							style={{
								display: "block",
								marginBottom: 6,
								fontSize: 13,
							}}>
							About you
						</label>
						<textarea
							value={profileSummary}
							onChange={(e) => setProfileSummary(e.target.value)}
							rows={5}
							style={{
								...inputStyle,
								resize: "vertical",
								marginBottom: 16,
							}}
						/>

						<div
							style={{
								display: "flex",
								justifyContent: "flex-end",
								alignItems: "center",
								gap: 10,
							}}>
							{saveStatus === "saved" && (
								<span
									style={{ fontSize: 13, color: "#20a67a" }}>
									Saved
								</span>
							)}
							{saveStatus === "error" && (
								<span
									style={{ fontSize: 13, color: "#e05252" }}>
									Failed to save
								</span>
							)}
							<button
								onClick={saveProfile}
								disabled={saveStatus === "saving"}
								style={{
									border: "none",
									borderRadius: 8,
									background: "#5b84ff",
									color: "white",
									padding: "8px 16px",
									cursor:
										saveStatus === "saving"
											? "not-allowed"
											: "pointer",
									fontWeight: 600,
									opacity: saveStatus === "saving" ? 0.7 : 1,
								}}>
								{saveStatus === "saving" ? "Saving…" : "Save"}
							</button>
						</div>
					</aside>
				</div>
			)}
		</main>
	)
}

export default OptionsPage
