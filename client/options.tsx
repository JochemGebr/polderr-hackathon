import { useEffect, useMemo, useState } from "react"

const API_BASE = "http://localhost:3001/api"

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

	useEffect(() => {
		chrome.storage.local.get("userId", async (result) => {
			const id = result.userId as string | undefined
			if (!id) return
			setUserId(id)
			const res = await fetch(`${API_BASE}/users/${id}`)
			if (!res.ok) return
			const user = await res.json()
			if (user.name) setProfileName(user.name)
			if (user.gender) setProfileGender(user.gender)
			if (user.occupation) setProfileOccupation(user.occupation)
			if (user.income != null) setProfileIncome(String(user.income))
			if (user.age != null) setProfileAge(String(user.age))
			setProfileHasPets(user.has_pets ?? false)
			if (user.bio) setProfileSummary(user.bio)
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
				bio: profileSummary || null
			}
			if (userId) {
				const res = await fetch(`${API_BASE}/users/${userId}`, {
					method: "PUT",
					headers: { "Content-Type": "application/json" },
					body: JSON.stringify(body)
				})
				if (!res.ok) throw new Error("Update failed")
			} else {
				const res = await fetch(`${API_BASE}/users`, {
					method: "POST",
					headers: { "Content-Type": "application/json" },
					body: JSON.stringify(body)
				})
				if (!res.ok) throw new Error("Create failed")
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

	const weeklyApplications = [3, 4, 6, 5, 8, 7, 9]
	const responseRate = [22, 26, 31, 28, 34, 38, 41]
	const linePoints = useMemo(
		() =>
			responseRate
				.map((value, index) => {
					const x = 20 + index * 45
					const y = 120 - value * 2
					return `${x},${y}`
				})
				.join(" "),
		[responseRate]
	)

	return (
		<main
			style={{
				minHeight: "100vh",
				padding: 24,
				boxSizing: "border-box",
				background: "#f5f7fb",
				color: "#172033",
				fontFamily: "Montserrat, -apple-system, BlinkMacSystemFont, sans-serif"
			}}>
			<div style={{ maxWidth: 1200, margin: "0 auto" }}>
				<header
					style={{
						display: "flex",
						justifyContent: "space-between",
						alignItems: "center",
						marginBottom: 20
					}}>
					<div>
						<h1 style={{ margin: 0 }}>Dashboard</h1>
						<p style={{ margin: "4px 0 0", color: "#4b5874" }}>
							Track your job search performance at a glance
						</p>
					</div>
					<button
						onClick={() => setIsProfileOpen((current) => !current)}
						style={{
							border: "1px solid #c8d2ea",
							borderRadius: 10,
							background: "white",
							padding: "10px 14px",
							cursor: "pointer",
							fontWeight: 600
						}}>
						{isProfileOpen ? "Close profile" : "Profile"}
					</button>
				</header>

				<section
					style={{
						display: "grid",
						gridTemplateColumns: "repeat(4, minmax(0, 1fr))",
						gap: 12,
						marginBottom: 20
					}}>
					{[
						["Applications sent", "42", "+8 this week"],
						["Interview invites", "9", "21.4% conversion"],
						["Response rate", "41%", "+7% vs last week"],
						["Avg time to reply", "3.2 days", "-0.6 days"]
					].map(([title, value, subtitle]) => (
						<article
							key={title}
							style={{
								background: "white",
								borderRadius: 12,
								padding: 14,
								border: "1px solid #e5ebf8"
							}}>
							<h2 style={{ margin: 0, fontSize: 13, color: "#4b5874" }}>
								{title}
							</h2>
							<p style={{ margin: "8px 0 4px", fontSize: 28, fontWeight: 700 }}>
								{value}
							</p>
							<p style={{ margin: 0, fontSize: 12, color: "#4b5874" }}>
								{subtitle}
							</p>
						</article>
					))}
				</section>

				<section
					style={{
						display: "grid",
						gridTemplateColumns: "1fr 1fr",
						gap: 12
					}}>
					<article
						style={{
							background: "white",
							borderRadius: 12,
							border: "1px solid #e5ebf8",
							padding: 16
						}}>
						<h2 style={{ margin: "0 0 12px", fontSize: 16 }}>
							Weekly applications
						</h2>
						<div
							style={{
								height: 160,
								display: "flex",
								alignItems: "end",
								gap: 10
							}}>
							{weeklyApplications.map((value, index) => (
								<div key={`${value}-${index}`} style={{ flex: 1 }}>
									<div
										style={{
											height: `${value * 14}px`,
											background: "#5b84ff",
											borderRadius: "6px 6px 0 0"
										}}
									/>
									<p
										style={{
											margin: "8px 0 0",
											fontSize: 12,
											color: "#4b5874",
											textAlign: "center"
										}}>
										D{index + 1}
									</p>
								</div>
							))}
						</div>
					</article>

					<article
						style={{
							background: "white",
							borderRadius: 12,
							border: "1px solid #e5ebf8",
							padding: 16
						}}>
						<h2 style={{ margin: "0 0 12px", fontSize: 16 }}>
							Response rate trend (%)
						</h2>
						<svg viewBox="0 0 320 140" style={{ width: "100%", height: 170 }}>
							<line x1="20" y1="120" x2="300" y2="120" stroke="#dbe3f6" />
							<polyline
								fill="none"
								stroke="#20a67a"
								strokeWidth="3"
								points={linePoints}
							/>
							{responseRate.map((value, index) => {
								const x = 20 + index * 45
								const y = 120 - value * 2
								return <circle key={`${x}-${y}`} cx={x} cy={y} r="4" fill="#20a67a" />
							})}
						</svg>
					</article>
				</section>

				{isProfileOpen ? (
					<div
						style={{
							position: "fixed",
							inset: 0,
							background: "rgba(10, 18, 38, 0.45)",
							display: "flex",
							alignItems: "center",
							justifyContent: "center",
							padding: 16
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
								overflowY: "auto"
							}}>
							<div
								style={{
									display: "flex",
									justifyContent: "space-between",
									alignItems: "center",
									marginBottom: 12
								}}>
								<h2 style={{ margin: 0, fontSize: 16 }}>Profile</h2>
								<button
									onClick={() => setIsProfileOpen(false)}
									style={{
										border: "1px solid #c8d2ea",
										borderRadius: 8,
										background: "white",
										padding: "6px 10px",
										cursor: "pointer"
									}}>
									Close
								</button>
							</div>

							<label style={{ display: "block", marginBottom: 8, fontSize: 13 }}>
								Name
							</label>
							<input
								value={profileName}
								onChange={(e) => setProfileName(e.target.value)}
								style={{
									width: "100%",
									border: "1px solid #c8d2ea",
									borderRadius: 8,
									padding: "8px 10px",
									marginBottom: 12,
									boxSizing: "border-box"
								}}
							/>

							<div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginBottom: 12 }}>
								<div>
									<label style={{ display: "block", marginBottom: 8, fontSize: 13 }}>
										Gender
									</label>
									<input
										value={profileGender}
										onChange={(e) => setProfileGender(e.target.value)}
										style={{
											width: "100%",
											border: "1px solid #c8d2ea",
											borderRadius: 8,
											padding: "8px 10px",
											boxSizing: "border-box"
										}}
									/>
								</div>
								<div>
									<label style={{ display: "block", marginBottom: 8, fontSize: 13 }}>
										Age
									</label>
									<input
										type="number"
										value={profileAge}
										onChange={(e) => setProfileAge(e.target.value)}
										style={{
											width: "100%",
											border: "1px solid #c8d2ea",
											borderRadius: 8,
											padding: "8px 10px",
											boxSizing: "border-box"
										}}
									/>
								</div>
							</div>

							<label style={{ display: "block", marginBottom: 8, fontSize: 13 }}>
								Occupation
							</label>
							<input
								value={profileOccupation}
								onChange={(e) => setProfileOccupation(e.target.value)}
								style={{
									width: "100%",
									border: "1px solid #c8d2ea",
									borderRadius: 8,
									padding: "8px 10px",
									marginBottom: 12,
									boxSizing: "border-box"
								}}
							/>

							<label style={{ display: "block", marginBottom: 8, fontSize: 13 }}>
								Monthly income (€)
							</label>
							<input
								type="number"
								value={profileIncome}
								onChange={(e) => setProfileIncome(e.target.value)}
								style={{
									width: "100%",
									border: "1px solid #c8d2ea",
									borderRadius: 8,
									padding: "8px 10px",
									marginBottom: 12,
									boxSizing: "border-box"
								}}
							/>

							<label
								style={{
									display: "flex",
									alignItems: "center",
									gap: 8,
									marginBottom: 12,
									fontSize: 13,
									cursor: "pointer"
								}}>
								<input
									type="checkbox"
									checked={profileHasPets}
									onChange={(e) => setProfileHasPets(e.target.checked)}
								/>
								Has pets
							</label>

							<label style={{ display: "block", marginBottom: 8, fontSize: 13 }}>
								About you
							</label>
							<textarea
								value={profileSummary}
								onChange={(event) => setProfileSummary(event.target.value)}
								rows={6}
								style={{
									width: "100%",
									border: "1px solid #c8d2ea",
									borderRadius: 8,
									padding: "8px 10px",
									resize: "vertical",
									boxSizing: "border-box",
									marginBottom: 16
								}}
							/>

							<div
								style={{
									display: "flex",
									justifyContent: "flex-end",
									alignItems: "center",
									gap: 10
								}}>
								{saveStatus === "saved" && (
									<span style={{ fontSize: 13, color: "#20a67a" }}>
										Saved
									</span>
								)}
								{saveStatus === "error" && (
									<span style={{ fontSize: 13, color: "#e05252" }}>
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
										opacity: saveStatus === "saving" ? 0.7 : 1
									}}>
									{saveStatus === "saving" ? "Saving…" : "Save"}
								</button>
							</div>
						</aside>
					</div>
				) : null}
			</div>
		</main>
	)
}

export default OptionsPage
