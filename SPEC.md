# UAE Household Expense Tracker — Project Spec

## Overview
A mobile-first web app for UAE households to track grocery and household
spending. All receipts — physical and online — are uploaded as photos or
screenshots. Gemini Flash parses them end-to-end (image to structured JSON
in one API call), with native Arabic/English support. Includes monthly AED
budget reporting and halal categorization.

---

## Tech Stack
- Frontend: React + Vite + Tailwind CSS (mobile-first)
- Backend: FastAPI (Python)
- Database: PostgreSQL (Supabase free tier)
- File Storage: Supabase Storage (free tier, 1GB)
- Receipt Parsing: Google Gemini 1.5 Flash (free tier — 1,500 req/day)
  - Multimodal: image → structured JSON in one API call
  - Handles photos AND screenshots equally well
  - Handles Arabic/English mixed text natively
- Auth: Supabase Auth (free tier)
- Deployment: Docker Compose (dev), Vercel (frontend), Render.com (backend)
- Notifications: Resend free tier (100 emails/day) for alerts

---

## Core Entities
- User (household account, multi-user support)
- Receipt (store, date, total_aed, source: physical_photo / online_screenshot / manual)
- LineItem (receipt_id, name, quantity, unit_price, category, is_halal)
- Store (name, type: physical/online, logo)
- PriceHistory (item_name, store_id, price, date)
- Budget (user_id, month, category, limit_aed)

---

## Milestone 1 — Physical Receipt Upload & Parsing

### Features
1. User signup / login (Supabase Auth)
2. Upload 1–5 photos for a single physical receipt (multi-photo stitching
   for long receipts)
3. Send photo(s) directly to Gemini Flash — no separate OCR step
4. Gemini returns structured JSON:
   - Store name
   - Total amount in AED
   - Line items: name, quantity, unit_price, category, is_halal
5. Show extracted items in editable review screen
6. User confirms or corrects items
7. Receipt saved to Supabase DB with all line items
8. Show mismatch warning if sum of items != receipt total

---

## Milestone 2 — Online Order Screenshot Upload

### Features
1. Upload screenshot(s) of online order confirmations from:
   - noon.com
   - amazon.ae
   - carrefouruae.com app/website
   - instashop.ae
   - talabat groceries
   - any other UAE online retailer
2. Same Gemini Flash parsing flow as Milestone 1 — the model handles
   screenshots and photos with the same prompt
3. Tag receipt source as "online_screenshot" automatically
4. Capture delivery fee and VAT as separate line items if visible in screenshot
5. Same review + confirm flow as physical receipts
6. Multi-screenshot support for long order summaries (e.g. scrolling through
   a noon order with many items)

### Why screenshots only (no Gmail OAuth)
- Simpler architecture — no OAuth, no token refresh, no Gmail API quotas
- User has full control over what gets uploaded
- No background email scanning — better for privacy
- Works regardless of which email account received the order
- Works for orders placed via apps that don't email confirmations

---

## Milestone 3 — Price Tracking & Budget Reports

### Features
1. Price history tracked per item+store combination across both physical
   and online sources
2. Alert when a frequently bought item price increases >10%
3. Cross-store price comparison for identical items (e.g. compare Lulu
   in-store vs Carrefour online for the same product)
4. Monthly dashboard:
   - Total spend this month vs last month (AED)
   - Spend by category (pie chart)
   - Spend by store (bar chart)
   - Spend by source (physical vs online split)
   - Top 10 most purchased items
   - Halal vs non-halal spend split
5. Monthly PDF report export
6. Budget limits per category with progress bars
7. Summary mode: log total + store + date without item detail

---

## Free Stack Cost Breakdown
| Component         | Service                    | Cost   |
|-------------------|----------------------------|--------|
| Frontend hosting  | Vercel free tier           | $0     |
| Backend hosting   | Render.com free tier       | $0     |
| Database          | Supabase free tier         | $0     |
| File storage      | Supabase Storage           | $0     |
| Auth              | Supabase Auth              | $0     |
| Receipt parsing   | Gemini Flash (1500/day)    | $0     |
| Email alerts      | Resend free tier           | $0     |
| TOTAL             |                            | $0/mo  |

---

## Non-Functional Requirements
- Mobile-first UI, works well on 390px screen width
- All monetary values stored and displayed in AED
- Supports Arabic product names (display only, no RTL UI needed)
- Receipt images stored in Supabase Storage, not in DB
- JWT tokens managed by Supabase Auth
- Dockerized with docker-compose.yml for local dev
- Vercel for frontend, Render.com for backend in prod
- Environment variables via .env (never committed)
- Unit tests for Gemini parser (mocked)

---

## Project Structure
expense-tracker/
├── frontend/          # React + Vite app (deployed to Vercel)
├── backend/           # FastAPI app (deployed to Render.com)
│   ├── routers/
│   ├── models/
│   ├── services/
│   │   ├── gemini_parser.py   # Gemini Flash receipt parser
│   │   └── price_tracker.py
│   └── main.py
├── docker-compose.yml
├── SPEC.md
├── CLAUDE.md
└── .env.example
