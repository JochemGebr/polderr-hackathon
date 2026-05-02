# CrowdApply

Browser extension + FastAPI backend for drafting smarter Kamernet applications. The extension extracts listing details, the backend scores match signals and generates a draft message.

## Repository layout

- client/ - Plasmo browser extension (popup UI, listing extraction)
- server/ - FastAPI backend (match scoring + message generation)

## Quick start

### Backend (FastAPI)

```bash
cd server
cp .env.example .env
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 3001
```

Docs: http://localhost:3001/docs

### Extension (Plasmo)

```bash
cd client
npm install
npm run dev
```

Load the dev build in Chrome:

- chrome://extensions
- Enable Developer mode
- Load unpacked -> client/build/chrome-mv3-dev

## How it works

1. Open a Kamernet listing.
2. Popup reads the listing content and posts it to the backend.
3. Backend returns match signals and a generated message draft.

## Notes

- Backend expects `external_id` to be the numeric ID from the listing URL.
- The extension points to the API at http://localhost:3001 by default.

## Development tips

- Edit popup UI in client/popup.tsx and styles in client/popup.css.
- Backend entry point is server/app/main.py.
