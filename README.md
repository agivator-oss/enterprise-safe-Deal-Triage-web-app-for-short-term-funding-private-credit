## Deal Triage (MVP)

Enterprise-safe decision support web app for short-term funding / private credit.

### What it does
- Create deals
- Upload documents (PDF/DOCX/TXT)
- Extract structured terms (LLM-assisted; stub by default)
- Deterministic analysis (LVR + explainable red-flag rules)
- IC-style draft (LLM-assisted; stub by default)
- Export a basic PDF summary

### Local dev (Docker)

Prereqs: Docker + Docker Compose.

```bash
docker compose up --build
```

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000/health`
- Postgres: `localhost:5432` (postgres/postgres)

### Notes
- **No external LLM calls** happen unless you configure `LLM_PROVIDER=azure` and provide Azure OpenAI env vars.
- Redaction is applied before LLM calls and before persisting LLM outputs.
- Extracted document text is stored in DB (MVP) with a TODO for encryption-at-rest.

### Backend tests

If you run locally (non-docker), create a venv and install requirements in `backend/`.

```bash
cd backend
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
pytest
```
