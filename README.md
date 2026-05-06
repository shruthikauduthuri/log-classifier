# Log Noise Classifier

AI-powered log relevance scoring and SIEM routing dashboard. The app uses a Flask API to keep the Gemini API key server-side, and a React/Vite dashboard for uploading logs, watching batch progress, and exporting classification results.

## What It Does

- Scores log lines with `gemini-2.5-pro`.
- Routes events to `SIEM`, `DataLake`, or `ColdStorage` using configurable thresholds.
- Shows KPI cards, routing bars, source volume charts, savings estimates, and a sortable classification table.
- Exports complete results as CSV and a one-page PDF summary.
- Enforces free-tier guardrails by default to avoid accidental Gemini quota burn.

## Repo Layout

```text
backend/   Flask API, Gemini integration, validation, security controls, tests
frontend/  React + Vite dashboard, charts, exports, UI tests
.github/   CI workflow for backend and frontend validation
```

## Security Model

- `GEMINI_API_KEY` is read only by the backend from environment variables.
- The key is never sent to the browser, logged, or included in API responses.
- `.env` files are ignored by Git; use `backend/.env.example` as the template.
- CORS is whitelist-only via `ALLOWED_ORIGINS`.
- Uploaded files are parsed in memory and are never written to disk.
- Rate limits, request limits, file size limits, and security headers are enabled by default.
- Gemini provider errors are sanitized before returning to clients.

## Free-Tier Guardrails

The PRD allows large uploads, but this implementation defaults to safer limits for Gemini free-tier usage:

```text
MAX_LOG_LINES_PER_REQUEST=100
GEMINI_BATCH_SIZE=20
GEMINI_MAX_CALLS_PER_REQUEST=5
MAX_FILE_SIZE_MB=5
```

For paid tiers or controlled demos, raise these values in the backend environment. Keep `GEMINI_MODEL=gemini-2.5-pro`.

## Local Setup

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# edit .env and set GEMINI_API_KEY
flask --app wsgi.py run --host 0.0.0.0 --port 5001
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. The Vite dev server proxies `/api` to `http://localhost:5001`.

If either port is occupied, keep the ports aligned:

```bash
# backend on 5002
cd backend
flask --app wsgi.py run --host 127.0.0.1 --port 5002

# frontend proxying to that backend
cd frontend
VITE_PROXY_API_TARGET=http://127.0.0.1:5002 npm run dev
```

When using `VITE_API_BASE_URL` for direct browser-to-backend calls, add the actual frontend URL to `ALLOWED_ORIGINS` in `backend/.env`.

## Docker Compose

```bash
cp backend/.env.example backend/.env
# edit backend/.env and set GEMINI_API_KEY
docker compose up --build
```

Frontend: `http://localhost:5173`

Backend health: `http://localhost:5001/api/health`

## API

### `GET /api/health`

Returns app status, configured model, whether a Gemini key is present, and limit settings. Add `?check=live` to request a live provider check.

### `POST /api/classify`

Accepts JSON:

```json
{
  "logs": ["May 5 host sshd[1200]: Failed password for root"],
  "source_hint": "Auth",
  "high_threshold": 0.7,
  "medium_threshold": 0.4
}
```

Also accepts multipart form data with a `.txt` or `.log` file field named `file`.

### `POST /api/classify/stream`

Same request shape, returns newline-delimited JSON events:

- `accepted`
- `batch_complete`
- `complete`
- `error`

## Validation

```bash
cd backend
pytest --cov=app --cov-report=term-missing --cov-fail-under=80

cd ../frontend
npm run lint
npm test -- --run
npm run build
```

## Environment

See [backend/.env.example](backend/.env.example).
