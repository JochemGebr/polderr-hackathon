import { useMemo, useState } from "react"

function OptionsPage() {
	const [isProfileOpen, setIsProfileOpen] = useState(false)
	const [profileName, setProfileName] = useState("Alex Candidate")
	const [profileSummary, setProfileSummary] = useState(
		"Product-minded software engineer with 6+ years building web apps. Looking for remote-friendly teams where I can contribute across frontend and product analytics."
	)

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
								onChange={(event) => setProfileName(event.target.value)}
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
									boxSizing: "border-box"
								}}
							/>
						</aside>
					</div>
				) : null}
			</div>
		</main>
	)
}

export default OptionsPage
