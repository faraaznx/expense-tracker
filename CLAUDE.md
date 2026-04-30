# CLAUDE.md — UAE Expense Tracker

## About Me
I am a data/platform engineer comfortable with Python, Docker, and FastAPI.
I understand backend architecture well but want you to suggest the best
patterns for this specific app. I prefer production-grade code over quick hacks.

## How I Want You to Work

### Always plan before coding
- Before writing any code, explain what you're about to do and why
- If there are multiple approaches, present the top 2 with tradeoffs
- Wait for my confirmation before proceeding
- Break large tasks into small, testable steps

### Code quality
- All FastAPI endpoints must have Pydantic v2 request and response models
- All DB queries via SQLAlchemy async ORM (never raw SQL unless I ask)
- Use dependency injection for DB sessions and auth
- Every service function must have a docstring explaining inputs/outputs
- No hardcoded values — use environment variables via pydantic-settings
- Raise proper HTTPException with meaningful status codes and messages

### File structure
- Keep routers thin — business logic lives in services/
- One file per domain: receipts, items, stores, budgets, users
- Shared utilities in utils/
- Never put logic in main.py

### Testing
- After each feature, write at least one pytest unit test
- Mock external APIs (Gemini, Supabase)
- Remind me to test parsing on a real Lulu/Carrefour photo AND a real
  noon/amazon.ae screenshot after each parser change

### Docker
- Always keep docker-compose.yml working for local dev
- No local model serving needed — Gemini is a cloud API

## Project-Specific Rules

### Currency
- All monetary values are in AED
- Store prices as Numeric(10,2) in PostgreSQL — never float
- Display format: "AED 12.50" in UI

### Receipt Sources
- Physical receipts: photos taken with phone camera
- Online orders: screenshots of order confirmation pages or app screens
- Both go through the same Gemini Flash parsing pipeline
- Tag source field as "physical_photo" or "online_screenshot" — this
  matters for analytics later
- Never integrate Gmail OAuth or any email scanning — user uploads
  everything manually

### Receipt Parsing
- Use Gemini 1.5 Flash via google-generativeai Python SDK
- Send images directly to Gemini — no separate OCR step
- Always show user a review screen before saving
- If sum of extracted line items does not match receipt total, show a
  warning with the difference amount in AED
- Never auto-save a receipt without user confirmation

### Gemini API Usage
- Model: gemini-1.5-flash (free tier — 1,500 req/day, 15 req/min)
- Always instruct the model to return ONLY valid JSON — no preamble,
  no markdown fences
- Wrap all Gemini API calls in try/except and handle failures gracefully
- Log the raw Gemini response before parsing so I can debug issues
- Strip any leading/trailing markdown fences (```json ... ```) before
  json.loads() — Gemini sometimes adds them despite instructions
- Implement retry with exponential backoff on rate limit errors
- Cache identical image hashes to avoid re-parsing the same receipt

### Halal Categorization
- is_halal defaults to true for produce, dairy, dry goods
- is_halal defaults to false for items containing: pork, lard, gelatin,
  alcohol, wine, beer in the name
- is_halal is null (unknown) for ambiguous items — do not guess
- Never override a user's manual correction to is_halal

### Privacy
- Receipt images stored in Supabase Storage only — never in the DB
- Store only the Supabase Storage path in the receipts table
- Signed URLs expire in 1 hour when serving images to frontend
- Receipt images are sent to Google's Gemini API for parsing —
  document this clearly in the privacy policy
- No analytics or telemetry of any kind
- No background email scanning, no OAuth integrations — user uploads
  everything explicitly

## Environment
- Local dev: Docker Compose with hot reload
- Frontend: Vercel (free tier)
- Backend: Render.com (free tier)
- Database + Auth + Storage: Supabase (free tier)
- Receipt parsing: Google Gemini 1.5 Flash (free tier)
- Python base image: python:3.11-slim

## Required Environment Variables
- GEMINI_API_KEY — from aistudio.google.com (free, no credit card)
- SUPABASE_URL
- SUPABASE_ANON_KEY
- SUPABASE_SERVICE_KEY
- DATABASE_URL
- RESEND_API_KEY (for email alerts)

## Preferred Libraries
- FastAPI + Uvicorn
- SQLAlchemy 2.x async
- Pydantic v2
- Alembic for migrations
- httpx for async HTTP calls
- Pillow for image processing
- google-generativeai (official Gemini SDK)
- supabase-py (official Supabase Python client)
- pytest + pytest-asyncio for tests
- React + Vite + Tailwind CSS for frontend
- lucide-react for icons only

## UI Design Standards
- Mobile-first, all layouts must work on 390px screen width
- Color palette: warm whites, deep greens, AED gold accents
- Cards with subtle shadows, rounded-xl corners, generous padding
- Receipt review screen must feel like a native mobile app, not a web form
- No tables — use card lists for receipt line items on mobile
- Upload screen should treat photos and screenshots identically — one
  upload button, no source toggle needed

## What I Don't Want
- No unnecessary abstractions or over-engineering on milestone 1
- No placeholder comments like "add logic here" — write real code
  or tell me it needs a decision first
- No npm packages with known security vulnerabilities
- Don't suggest paid services — keep everything on the free stack
- Don't switch APIs or libraries mid-milestone without discussing first
- Do not bring back Tesseract or Ollama — Gemini handles parsing end-to-end
- Do not add Gmail OAuth, IMAP, or any email scanning — screenshots only
