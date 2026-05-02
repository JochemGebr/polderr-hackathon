# CrowdApply — Backend

FastAPI backend for the CrowdApply browser extension. Stores Kamernet listings, user profiles, and crowdsourced application outcomes, then uses feature-correlation to generate personalised application messages.

## Setup

```bash
cp .env.example .env
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 3001
```

Database (SQLite) is created automatically on first start. Interactive docs at **http://localhost:3001/docs**.

---

## API Reference

### Listings

| Method | Path | Body / Params | Description |
|--------|------|---------------|-------------|
| `POST` | `/api/listings` | `ListingCreate` | Create or update a listing (idempotent on `external_id`) |
| `GET` | `/api/listings/{listing_id}` | — | Get a listing by ID |
| `POST` | `/api/listings/{listing_id}/features/{feature_id}` | — | Tag a feature onto a listing |
| `DELETE` | `/api/listings/{listing_id}/features/{feature_id}` | — | Remove a feature tag from a listing |

**`ListingCreate`**
```json
{
  "external_id": "2373935",
  "url": "https://kamernet.nl/huren/kamer-delft/...",
  "title": "Kamer Hendrik Tollensstraat",
  "description": "Full listing description text...",

  "price": 90000,
  "utilities_included": true,

  "location": "Delft",
  "listing_type": "room",
  "size_m2": 14,
  "furnished": true,
  "available_from": "2026-08-01",
  "min_duration_months": 3,

  "age_min": 16,
  "age_max": 35,
  "gender_preference": "female",
  "accepted_occupations": ["student", "working_student", "employed"],
  "max_tenants": 1,
  "language": "English",
  "pets_allowed": false,

  "accepted_person_id": null
}
```
> All fields except `external_id`, `url`, `title`, and `description` are optional — send what the scraper can find.
> `price` is in **euro cents** (€900 = `90000`).
> `external_id` = the numeric listing ID from the Kamernet URL (`kamer-2373935` → `"2373935"`).
> `gender_preference`: `"any"` | `"male"` | `"female"`.
> `accepted_occupations`: any subset of `["student", "working_student", "employed", "job_seeker"]`.

---

### Users

| Method | Path | Body | Description |
|--------|------|------|-------------|
| `POST` | `/api/users` | `UserCreate` | Create a user profile |
| `GET` | `/api/users/{user_id}` | — | Get a user by ID |
| `PUT` | `/api/users/{user_id}` | `UserUpdate` | Update a user profile |

**`UserCreate` / `UserUpdate`**
```json
{
  "name": "Jan de Vries",
  "occupation": "Software Engineer",
  "income": 3500,
  "age": 28,
  "has_pets": false,
  "bio": "Quiet professional, working from home 3 days a week.",
  "profile": { "contract_type": "permanent", "languages": ["NL", "EN"] }
}
```

---

### Applications

| Method | Path | Body | Description |
|--------|------|------|-------------|
| `POST` | `/api/applications` | `ApplicationCreate` | Record an application (idempotent on user+listing pair) |
| `PATCH` | `/api/applications/{application_id}` | `ApplicationUpdate` | Update status or add result notes |
| `GET` | `/api/applications/user/{user_id}` | — | All applications for a user |

**`ApplicationCreate`**
```json
{
  "user_id": "...",
  "listing_id": "...",
  "message": "Geachte verhuurder, ..."
}
```

**`ApplicationUpdate`** — all fields optional
```json
{
  "status": "ACCEPTED",
  "message": "Updated draft...",
  "result_notes": "Landlord said they preferred a working professional"
}
```

> Valid statuses: `PENDING` · `INVITED` · `REJECTED` · `GHOSTED` · `ACCEPTED`

---

### Features

| Method | Path | Body | Description |
|--------|------|------|-------------|
| `POST` | `/api/features` | `FeatureCreate` | Create a feature |
| `GET` | `/api/features` | — | List all features |
| `GET` | `/api/features/{feature_id}` | — | Get a feature by ID |

**`FeatureCreate`**
```json
{
  "name": "prefers_working_professional",
  "description": "Landlord explicitly or implicitly prefers employed tenants over students"
}
```

---

### Persons

Persons represent applicant profiles from crowdsourced historical data (distinct from `User`, which is the app's own user).

| Method | Path | Body | Description |
|--------|------|------|-------------|
| `POST` | `/api/persons` | `PersonCreate` | Create a person |
| `GET` | `/api/persons/{person_id}` | — | Get a person by ID |
| `PUT` | `/api/persons/{person_id}` | `PersonCreate` | Update a person |
| `POST` | `/api/persons/{person_id}/features/{feature_id}` | — | Tag a feature onto a person |
| `DELETE` | `/api/persons/{person_id}/features/{feature_id}` | — | Remove a feature tag from a person |

**`PersonCreate`**
```json
{
  "name": "Anna",
  "age": 25,
  "gender": "F",
  "nationality": "NL",
  "text": "Working professional, no pets, non-smoker"
}
```

---

### Messages

Messages are historical application texts tied to a person and a listing (crowdsourced).

| Method | Path | Body | Description |
|--------|------|------|-------------|
| `POST` | `/api/messages` | `MessageCreate` | Create a message |
| `GET` | `/api/messages/{message_id}` | — | Get a message by ID |
| `GET` | `/api/messages/listing/{listing_id}` | — | All messages for a listing |
| `POST` | `/api/messages/{message_id}/features/{feature_id}` | — | Tag a feature onto a message |
| `DELETE` | `/api/messages/{message_id}/features/{feature_id}` | — | Remove a feature tag from a message |

**`MessageCreate`**
```json
{
  "person_id": "...",
  "listing_id": "...",
  "message": "Geachte verhuurder, mijn naam is Anna..."
}
```

---

### Recommendations

| Method | Path | Params | Description |
|--------|------|--------|-------------|
| `GET` | `/api/recommendations` | `?listing_id=&user_id=` | Generate a personalised application message for a user applying to a listing |

**Response**
```json
{
  "message": "Geachte verhuurder...",
  "key_strengths": ["Stable income", "No pets"],
  "addressed_concerns": ["Quiet lifestyle mentioned"]
}
```


