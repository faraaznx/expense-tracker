import asyncio
import json
import logging
from decimal import Decimal

import google.generativeai as genai
from fastapi import HTTPException

from config import settings
from schemas.receipt import GeminiDraftResponse, GeminiRawResponse
from utils.image_hash import compute_hash

logger = logging.getLogger(__name__)

_cache: dict[str, GeminiDraftResponse] = {}

SYSTEM_PROMPT = """You are a receipt parser for a UAE household expense tracker.
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
      "normalized_name": "string — generic product type, strip brand",
      "quantity": number,
      "unit_price_aed": number,
      "category": "Produce | Meat & Seafood | Dairy & Eggs | Bakery | Beverages | Frozen & Snacks | Dry Goods & Pantry | Cleaning & Household | Personal Care | Baby & Kids | Electronics | Delivery Fee | VAT | Other"
    }
  ]
}

Rules:
- date: use receipt date if visible, else today in YYYY-MM-DD
- total_aed: final amount paid (after discounts, VAT)
- source: physical_photo if a paper receipt, online_screenshot if order UI
- quantity defaults to 1 if not shown
- unit_price_aed: price per single unit
- Delivery Fee and VAT: capture as separate line items if visible"""


async def _call_gemini(model, parts: list):
    """Make a single Gemini API call via asyncio.to_thread."""
    return await asyncio.to_thread(model.generate_content, parts)


async def parse_receipt_images(image_bytes_list: list[bytes]) -> GeminiDraftResponse:
    """Parse receipt images using Gemini Flash.

    Args:
        image_bytes_list: List of raw image bytes (1–5 images).

    Returns:
        GeminiDraftResponse with parsed items and optional mismatch_aed.

    Raises:
        HTTPException 422: If Gemini returns non-parseable JSON.
        HTTPException 503: If Gemini rate limit is hit after all retries.
        HTTPException 502: On any other Gemini error.
    """
    cache_key = compute_hash(image_bytes_list)
    if cache_key in _cache:
        return _cache[cache_key]

    genai.configure(api_key=settings.gemini_api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")

    parts: list = [SYSTEM_PROMPT]
    for img_bytes in image_bytes_list:
        parts.append({"mime_type": "image/jpeg", "data": img_bytes})

    max_retries = 3
    last_exc: Exception | None = None
    for attempt in range(max_retries):
        try:
            response = await _call_gemini(model, parts)
            break
        except Exception as e:
            last_exc = e
            if "429" in str(e) or "exhausted" in str(e).lower():
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
            # Non-rate-limit error — wrap as 502
            logger.exception("Gemini API error: %s", e)
            raise HTTPException(status_code=502, detail="Receipt parsing service unavailable.")
    else:
        # All retries exhausted on rate limit
        if last_exc and ("429" in str(last_exc) or "exhausted" in str(last_exc).lower()):
            raise HTTPException(status_code=503, detail="Gemini rate limit reached. Try again shortly.")
        raise last_exc  # type: ignore[misc]

    raw_text = response.text
    logger.info("Gemini raw response: %s", raw_text)

    # Strip markdown fences Gemini sometimes adds despite instructions
    text = raw_text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:])
        if text.endswith("```"):
            text = text[: text.rfind("```")]

    try:
        data = json.loads(text)
        parsed = GeminiRawResponse(**data)
    except Exception:
        logger.error("Failed to parse Gemini response: %s", raw_text)
        raise HTTPException(status_code=422, detail="Gemini returned unreadable data.")

    item_sum = sum(item.quantity * item.unit_price_aed for item in parsed.items)
    total = parsed.total_aed
    mismatch = None if abs(item_sum - total) < Decimal("0.01") else abs(item_sum - total)

    draft = GeminiDraftResponse(
        temp_image_paths=[],
        store_name=parsed.store_name,
        date=parsed.date,
        total_aed=parsed.total_aed,
        source=parsed.source,
        items=parsed.items,
        item_sum_aed=item_sum,
        mismatch_aed=mismatch,
    )
    _cache[cache_key] = draft
    return draft
