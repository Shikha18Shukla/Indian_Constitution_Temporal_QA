# Temporal Legal QA frontend

React + TypeScript + Vite + Tailwind CSS interface for the existing FastAPI comparison backend. The UI calls the real `/api/health`, `/api/compare`, and `/api/history` endpoints. It does not generate, cache, or substitute answers in the browser.

## Requirements

- Node.js 20.19+ or 22.12+ and npm.
- FastAPI backend running at `http://127.0.0.1:8000`.
- The backend's Gemini key configured in the root `.env` or process environment. The frontend never receives the key.

## Configure and run

From this directory, copy `.env.example` to `.env.local` if you need to change the API settings. The default `/api` base uses Vite's local proxy to the FastAPI server. If the backend is hosted elsewhere, set `VITE_BACKEND_PROXY_TARGET` to its origin; `VITE_API_BASE_URL` can be set to an absolute API URL when that origin enables CORS.

```powershell
Copy-Item .env.example .env.local
npm install
npm run dev
```

Open the URL printed by Vite (normally `http://127.0.0.1:5173`).

Create and verify a production bundle:

```powershell
npm run build
npm run preview
```

## Behavior

- The backend health card reports the backend's local prerequisite status. It does not test Gemini with a generation request.
- Choose A, B, C, or a subset. The exact question and reference date are sent unchanged.
- Returned answers, citations, evidence passages, timing, System C selected versions, coverage, errors and abstention reasons are displayed from API responses.
- History is fetched from the backend's local JSONL store. A result can be exported as JSON.
- The interface does not assign correctness scores or imply that an answer is legally correct.
