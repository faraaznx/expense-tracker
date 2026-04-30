# UAE Expense Tracker — Design Document
**Date:** 2026-04-30  
**Scope:** All 3 milestones (M1 planned first)  
**Status:** Approved

---

## Context

A greenfield mobile-first web app for a UAE household to track grocery and household spending. Users upload photos of physical receipts or screenshots of online orders; Google Gemini Flash parses them into structured data. The app stores receipts, tracks price changes per product over time, and provides a monthly AED spending dashboard with budget limits.

Nothing has been built yet. This document defines the full system design across all three milestones. Implementation begins with M1.

---

## Key Decisions

| Decision | Choice | Reason |
|---|---|---|
| Architecture | Backend-first REST API | All logic testable in Python; matches CLAUDE.md guidelines |
| Auth | Supabase Auth — email + password | Simple, free, JWT issued by Supabase verified by FastAPI |
| Multi-user | Each user is independent | No household sharing, no invite system needed |
| Multi-photo | Multiple images in one Gemini call | No stitching overhead; Gemini sees each photo at full resolution |
| Price alerts | In-app only, no email | Removes Resend dependency entirely |
| Categories | Fixed list (14 categories) | Consistent data for analytics from day one |
| Halal feature | Removed | Out of scope |
| Price comparison | Cross-store, any price change | Compare normalized product name across all stores, both directions |

---

## System Architecture

```
┌─────────────────────┐     JWT      ┌──────────────────────┐
│  Frontend           │ ──────────── │  FastAPI Backend      │
│  React + Vite       │  REST/JSON   │  Python 3.11          │
│  Tailwind CSS       │ ──────────── │  Render.com (free)    │
│  Vercel (free)      │              └──────────┬───────────┘
└─────────────────────┘                         │
                                    ┌───────────┼────────────┐
                              ┌─────┴─────┐ ┌──┴──────┐ ┌───┴──────┐
                              │ Supabase  │ │Supabase │ │  Gemini  │
                              │ Auth      │ │ Postgres│ │  Flash   │
                              │           │ │ Storage │ │  API     │
                              └───────────┘ └─────────┘ └──────────┘
```

### Key Data Flows

| Flow | Path |
|---|---|
| **Auth** | Frontend → Supabase Auth → JWT → sent with every request → FastAPI verifies |
| **Upload** | Frontend sends image(s) → FastAPI → Supabase Storage (temp/) + Gemini Flash |
| **Parse** | Gemini returns JSON → FastAPI validates → returns draft (nothing saved yet) |
| **Confirm** | User edits draft → POST /api/receipts → FastAPI saves to DB, moves images to permanent path |
| **Alerts** | On save → FastAPI checks price_history → creates Notification if price changed |

---

## Data Model

All monetary fields: `NUMERIC(10,2)`. Auth managed by Supabase (`auth.users`); no separate users table.

### stores
| Field | Type | Notes |
|---|---|---|
| id | UUID PK | |
| name | VARCHAR(255) UNIQUE | Case-insensitive lookup on receipt save |
| type | ENUM(physical, online) | Inferred from receipt source |
| logo_url | VARCHAR(500) nullable | |
| created_at | TIMESTAMPTZ | |

Auto-created when Gemini returns a store name not yet in the DB.

### receipts
| Field | Type | Notes |
|---|---|---|
| id | UUID PK | |
| user_id | UUID | FK → auth.users.id |
| store_id | UUID | FK → stores.id |
| date | DATE | Receipt date from Gemini |
| total_aed | NUMERIC(10,2) | Final amount paid |
| source | ENUM(physical_photo, online_screenshot, manual) | |
| created_at | TIMESTAMPTZ | |

### receipt_images
| Field | Type | Notes |
|---|---|---|
| id | UUID PK | |
| receipt_id | UUID | FK → receipts.id |
| storage_path | VARCHAR(500) | Supabase Storage path |
| display_order | SMALLINT | Ordering for multi-photo receipts |
| created_at | TIMESTAMPTZ | |

Separate table supports 1–5 ordered images per receipt. Signed URLs (1hr expiry) generated at query time, never stored.

### line_items
| Field | Type | Notes |
|---|---|---|
| id | UUID PK | |
| receipt_id | UUID | FK → receipts.id |
| name | VARCHAR(500) | Raw display name (preserves Arabic, brand) |
| normalized_name | VARCHAR(500) | Brand-stripped product type — used for price matching |
| quantity | NUMERIC(8,3) DEFAULT 1 | |
| unit_price_aed | NUMERIC(10,2) | Per single unit |
| category | VARCHAR(100) | From fixed list below |
| created_at | TIMESTAMPTZ | |

`total_price_aed` is a computed field in the Pydantic response model (`quantity × unit_price_aed`), not stored.

### price_history
| Field | Type | Notes |
|---|---|---|
| id | UUID PK | |
| user_id | UUID | FK → auth.users.id |
| normalized_name | VARCHAR(500) | Matches line_items.normalized_name |
| store_id | UUID | FK → stores.id |
| price_aed | NUMERIC(10,2) | |
| date | DATE | Receipt date |
| receipt_id | UUID | FK → receipts.id |

Written on every receipt save. Per-user (consistent with "each user is independent"). Powers M3 cross-store price comparison.

### budgets
| Field | Type | Notes |
|---|---|---|
| id | UUID PK | |
| user_id | UUID | FK → auth.users.id |
| month | DATE | First day of month |
| category | VARCHAR(100) | |
| limit_aed | NUMERIC(10,2) | |

### notifications *(M3 only)*
| Field | Type | Notes |
|---|---|---|
| id | UUID PK | |
| user_id | UUID | FK → auth.users.id |
| item_name | VARCHAR(500) | Display name |
| store_id | UUID | FK → stores.id |
| old_price_aed | NUMERIC(10,2) | |
| new_price_aed | NUMERIC(10,2) | |
| read_at | TIMESTAMPTZ nullable | null = unread |
| created_at | TIMESTAMPTZ | |

---

## Fixed Category List

| Category | Notes |
|---|---|
| Produce | Fruits, vegetables |
| Meat & Seafood | |
| Dairy & Eggs | |
| Bakery | |
| Beverages | |
| Frozen & Snacks | |
| Dry Goods & Pantry | |
| Cleaning & Household | |
| Personal Care | |
| Baby & Kids | |
| Electronics | |
| Delivery Fee | Online orders |
| VAT | Online orders |
| Other | |

---

## API Surface

All endpoints except `/api/auth/signup` and `/api/auth/login` require `Authorization: Bearer <JWT>`. FastAPI dependency `get_current_user` verifies with Supabase Auth and returns `user_id`.

### Auth
```
POST /api/auth/signup
POST /api/auth/login
POST /api/auth/logout
```

### Receipts (M1)
```
POST /api/receipts/parse      # Upload images → get draft JSON (nothing saved)
POST /api/receipts            # Save confirmed receipt + line items
GET  /api/receipts            # List user's receipts (paginated)
GET  /api/receipts/{id}       # Receipt detail + line items + signed image URLs
DEL  /api/receipts/{id}       # Delete receipt
```

### Stores
```
GET  /api/stores              # List all stores (for M3 comparison)
```

### Dashboard & Price History (M3)
```
GET  /api/dashboard?month=YYYY-MM
GET  /api/price-history/{item_name}
```

### Budgets & Notifications (M3)
```
GET    /api/budgets
POST   /api/budgets
DEL    /api/budgets/{id}
GET    /api/notifications
PATCH  /api/notifications/{id}/read
```

---

## Backend File Structure

```
backend/
├── main.py                    # FastAPI app init, router registration only
├── config.py                  # pydantic-settings env vars
├── database.py                # SQLAlchemy async engine + session
├── dependencies.py            # get_current_user, get_db
├── routers/
│   ├── auth.py
│   ├── receipts.py
│   ├── stores.py
│   ├── dashboard.py           # M3
│   ├── budgets.py             # M3
│   └── notifications.py       # M3
├── services/
│   ├── gemini_parser.py       # Gemini API + caching + retry
│   ├── receipt_service.py     # save receipt, move images, write price_history
│   ├── store_service.py       # upsert store by name
│   ├── price_alert_service.py # M3: check price_history, create notifications
│   └── dashboard_service.py   # M3: aggregation queries
├── models/
│   ├── receipt.py             # SQLAlchemy ORM models
│   ├── store.py
│   ├── line_item.py
│   ├── price_history.py
│   ├── budget.py
│   └── notification.py
├── schemas/
│   ├── receipt.py             # Pydantic v2 request/response schemas
│   ├── store.py
│   ├── line_item.py
│   ├── auth.py
│   ├── dashboard.py           # M3
│   └── budget.py              # M3
└── utils/
    ├── supabase_storage.py    # upload, move, signed URL helpers
    └── image_hash.py          # SHA-256 cache key
```

---

## Gemini Integration

### Prompt
```
You are a receipt parser for a UAE household expense tracker.
Analyse the provided image(s) of a receipt or order confirmation.
Return ONLY valid JSON — no preamble, no markdown fences.

{
  "store_name": "string",
  "date": "YYYY-MM-DD",
  "total_aed": number,
  "source": "physical_photo | online_screenshot",
  "items": [
    {
      "name": "string — raw receipt text, preserve Arabic and brand name",
      "normalized_name": "string — generic product type, strip brand (e.g. Full Cream Milk 1L)",
      "quantity": number,
      "unit_price_aed": number,
      "category": "Produce | Meat & Seafood | Dairy & Eggs | Bakery | Beverages |
                   Frozen & Snacks | Dry Goods & Pantry | Cleaning & Household |
                   Personal Care | Baby & Kids | Electronics | Delivery Fee | VAT | Other"
    }
  ]
}

Rules:
- date: use receipt date if visible, else today in YYYY-MM-DD
- total_aed: final amount paid (after discounts, VAT)
- source: physical_photo if a paper receipt, online_screenshot if order UI
- quantity defaults to 1 if not shown
- unit_price_aed: price per single unit (not quantity × price)
- Delivery Fee and VAT: capture as separate line items if visible
```

### Parser Logic (gemini_parser.py)
1. Compute SHA-256 of all image bytes concatenated → check in-memory cache
2. If cache hit: return immediately, no API call
3. Send all images + prompt to `gemini-1.5-flash` in one call
4. Log raw response text
5. Strip leading/trailing ` ```json ` fences
6. `json.loads()` → validate with Pydantic
7. Compute item sum, set `mismatch_aed` if sum ≠ total
8. Store in cache, return `GeminiDraftResponse`

### Error Handling
| Error | Action |
|---|---|
| 429 rate limit | Retry × 3: wait 1s → 2s → 4s, then raise HTTP 503 |
| JSON parse fails | Raise HTTP 422, log raw Gemini response |
| Any other error | Raise HTTP 502, log full exception |

### Draft Response Shape
```json
{
  "temp_image_paths": ["receipts/temp/uuid1.jpg"],
  "store_name": "Lulu Hypermarket",
  "date": "2026-04-28",
  "total_aed": 143.50,
  "source": "physical_photo",
  "items": [
    {
      "name": "Lacnor Full Cream Milk 1L",
      "normalized_name": "Full Cream Milk 1L",
      "quantity": 2,
      "unit_price_aed": 6.25,
      "total_price_aed": 12.50,
      "category": "Dairy & Eggs"
    }
  ],
  "item_sum_aed": 143.50,
  "mismatch_aed": null
}
```

`mismatch_aed` is non-null when item sum ≠ total_aed — frontend shows a warning banner. `temp_image_paths` are echoed back on confirm so the backend knows which Supabase paths to move.

---

## M1 — Receipt Upload & Parsing

### User Flow
1. User selects 1–5 images (single file input, no source toggle)
2. `POST /api/receipts/parse` — images uploaded to `receipts/temp/`, sent to Gemini
3. Draft JSON returned to frontend — **nothing written to DB**
4. Review screen: user edits items inline. Warning banner if `mismatch_aed` is non-null.
5. `POST /api/receipts` — confirmed data POSTed; backend saves Receipt + LineItems, moves images from `temp/` to `receipts/{user_id}/`, upserts Store, writes PriceHistory rows

### Receipt Confirm Service (receipt_service.py)
```
1. Begin transaction
2. Upsert store by name (case-insensitive) → get store_id
3. Insert Receipt row
4. Insert LineItem rows (with normalized_name)
5. Move Supabase Storage files: temp/ → receipts/{user_id}/
6. Insert receipt_images rows with display_order
7. Insert price_history rows for each line item
8. Commit
```

---

## M2 — Online Order Screenshots

No new endpoints, no schema changes. The same parse + confirm flow handles screenshots. Gemini infers `source = "online_screenshot"`. The only M2 addition is two hint lines in the Gemini prompt to capture Delivery Fee and VAT as line items (already in the category list).

---

## M3 — Price Tracking & Budget Reports

### Price Alert Logic (on receipt save)
```python
for item in confirmed_items:
    prev = latest price_history row for (user_id, item.normalized_name) across any store
    if prev exists and prev.price_aed != item.unit_price_aed:
        insert Notification(user_id, item.name, store_id,
                            old_price=prev.price_aed, new_price=item.unit_price_aed)
    insert PriceHistory row (always)
```

- Cross-store: previous price looked up across all stores by `(user_id, normalized_name)`
- Any change triggers an alert — both increases and decreases
- First purchase of a product: no alert

### Dashboard Response Shape
```json
{
  "month": "2026-04",
  "total_aed": 1843.20,
  "total_prev_month_aed": 1621.50,
  "by_category": [{"category": "Produce", "total_aed": 312.40}],
  "by_store": [{"store": "Lulu Hypermarket", "total_aed": 820.00}],
  "by_source": {"physical_photo": 1200.00, "online_screenshot": 643.20},
  "top_items": [{"name": "Full Cream Milk 1L", "count": 8, "total_aed": 50.00}],
  "budgets": [{"category": "Produce", "limit_aed": 400.00, "spent_aed": 312.40}]
}
```

### M3 New Work
- Price alert logic in `receipt_service.py`
- `dashboard_service.py` aggregation queries
- PDF export (WeasyPrint)
- Summary mode: `POST /api/receipts` with empty `items` array
- Frontend: Recharts for charts, budget progress bars, notifications bell icon

---

## Testing Strategy

### Mocks
- **Gemini API** — fixture JSON, never real calls in tests
- **Supabase Storage** — mock upload/move/signed URL
- **Supabase Auth** — dependency override returning a fake `user_id`
- **DB** — SQLite in-memory via SQLAlchemy async

### Key Test Cases

**test_gemini_parser.py**
- Valid response parses correctly
- Strips ```json fences before parse
- Malformed JSON → raises 422
- Rate limit (429) → retries 3× with backoff
- Item sum = total → `mismatch_aed` is null
- Item sum ≠ total → correct `mismatch_aed` returned
- Same image hash → returns cached result (no Gemini call)
- Arabic item names preserved
- `normalized_name` present on every item

**test_receipts.py**
- Confirm save creates Receipt + LineItems
- New store name → auto-creates Store row
- Known store name → reuses existing Store row
- Images moved from `temp/` → `receipts/{user_id}/`
- `total_price_aed` = quantity × unit_price in response
- GET receipts returns only current user's data
- GET receipt/{id} returns signed image URLs

**test_auth.py**
- No JWT → 401 on protected endpoints
- Invalid JWT → 401
- Valid JWT → request proceeds

**test_price_alerts.py** *(M3)*
- Price unchanged → no Notification created
- Price increased → Notification created
- Price decreased → Notification created
- Cross-store match on `normalized_name`
- Different `normalized_name` → no match, no alert
- First purchase → no alert

---

## Environment Variables

```
GEMINI_API_KEY
SUPABASE_URL
SUPABASE_ANON_KEY
SUPABASE_SERVICE_KEY
DATABASE_URL
```

Note: `RESEND_API_KEY` removed — in-app notifications only, no email.

---

## Non-Functional Requirements

- Mobile-first UI: all layouts work on 390px screen width
- All monetary values stored as `NUMERIC(10,2)`, displayed as "AED 12.50"
- Receipt images in Supabase Storage only — never in the DB
- Signed URLs expire in 1 hour
- Dockerized with `docker-compose.yml` for local dev
- Python base image: `python:3.11-slim`
- No analytics, no telemetry, no background email scanning
