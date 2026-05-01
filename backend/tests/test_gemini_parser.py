import json
from decimal import Decimal
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

FIXTURES = Path(__file__).parent / "fixtures"
TEST_IMAGE = b"fake-image-bytes"


def _load_fixture(name: str) -> str:
    return (FIXTURES / name).read_text()


@pytest.mark.asyncio
async def test_valid_response_parses_correctly():
    """A clean Gemini JSON response returns a GeminiDraftResponse."""
    from services.gemini_parser import parse_receipt_images

    raw_json = _load_fixture("lulu_receipt.json")
    mock_response = MagicMock()
    mock_response.text = raw_json

    with patch("services.gemini_parser._call_gemini", new_callable=AsyncMock) as mock_call:
        mock_call.return_value = mock_response
        result = await parse_receipt_images([TEST_IMAGE])

    assert result.store_name == "Lulu Hypermarket"
    assert len(result.items) == 3
    assert result.mismatch_aed is None


@pytest.mark.asyncio
async def test_strips_markdown_fences():
    """Gemini sometimes wraps JSON in ```json ... ``` — parser must strip them."""
    from services.gemini_parser import parse_receipt_images

    raw_json = _load_fixture("lulu_receipt.json")
    fenced = f"```json\n{raw_json}\n```"
    mock_response = MagicMock()
    mock_response.text = fenced

    with patch("services.gemini_parser._call_gemini", new_callable=AsyncMock) as mock_call:
        mock_call.return_value = mock_response
        result = await parse_receipt_images([TEST_IMAGE])

    assert result.store_name == "Lulu Hypermarket"


@pytest.mark.asyncio
async def test_malformed_json_raises_422():
    """If Gemini returns non-JSON, the parser raises HTTP 422."""
    from fastapi import HTTPException
    from services.gemini_parser import parse_receipt_images

    mock_response = MagicMock()
    mock_response.text = "Sorry, I cannot parse this image."

    with patch("services.gemini_parser._call_gemini", new_callable=AsyncMock) as mock_call:
        mock_call.return_value = mock_response
        with pytest.raises(HTTPException) as exc_info:
            await parse_receipt_images([TEST_IMAGE])

    assert exc_info.value.status_code == 422


@pytest.mark.asyncio
async def test_rate_limit_retries_three_times():
    """A 429-like error retries up to 3 times with backoff."""
    from services import gemini_parser
    from services.gemini_parser import parse_receipt_images

    gemini_parser._cache.clear()

    with patch("services.gemini_parser._call_gemini", new_callable=AsyncMock) as mock_call:
        mock_call.side_effect = Exception("429 Resource exhausted")
        with patch("asyncio.sleep", new_callable=AsyncMock):
            with pytest.raises(Exception):
                await parse_receipt_images([TEST_IMAGE])

    assert mock_call.call_count == 3


@pytest.mark.asyncio
async def test_mismatch_detected_when_sum_differs():
    """When item sum != total_aed, mismatch_aed is set to the difference."""
    from services.gemini_parser import parse_receipt_images

    data = json.loads(_load_fixture("lulu_receipt.json"))
    data["total_aed"] = 30.00  # actual sum is 25.00 → mismatch = 5.00
    mock_response = MagicMock()
    mock_response.text = json.dumps(data)

    with patch("services.gemini_parser._call_gemini", new_callable=AsyncMock) as mock_call:
        mock_call.return_value = mock_response
        result = await parse_receipt_images([TEST_IMAGE])

    assert result.mismatch_aed == Decimal("5.00")


@pytest.mark.asyncio
async def test_no_mismatch_when_sum_matches():
    """When item sum == total_aed, mismatch_aed is None."""
    from services.gemini_parser import parse_receipt_images

    raw_json = _load_fixture("lulu_receipt.json")
    mock_response = MagicMock()
    mock_response.text = raw_json

    with patch("services.gemini_parser._call_gemini", new_callable=AsyncMock) as mock_call:
        mock_call.return_value = mock_response
        result = await parse_receipt_images([TEST_IMAGE])

    assert result.mismatch_aed is None


@pytest.mark.asyncio
async def test_cache_returns_without_calling_gemini():
    """Identical image bytes hit the cache and skip the Gemini call."""
    from services import gemini_parser
    from services.gemini_parser import parse_receipt_images

    raw_json = _load_fixture("lulu_receipt.json")
    mock_response = MagicMock()
    mock_response.text = raw_json

    gemini_parser._cache.clear()

    with patch("services.gemini_parser._call_gemini", new_callable=AsyncMock) as mock_call:
        mock_call.return_value = mock_response
        await parse_receipt_images([TEST_IMAGE])
        await parse_receipt_images([TEST_IMAGE])

    assert mock_call.call_count == 1


@pytest.mark.asyncio
async def test_arabic_item_names_preserved():
    """Arabic text in item names is returned unchanged."""
    from services.gemini_parser import parse_receipt_images

    raw_json = _load_fixture("lulu_receipt.json")
    mock_response = MagicMock()
    mock_response.text = raw_json

    with patch("services.gemini_parser._call_gemini", new_callable=AsyncMock) as mock_call:
        mock_call.return_value = mock_response
        result = await parse_receipt_images([TEST_IMAGE])

    arabic_item = next(i for i in result.items if "خبز" in i.name)
    assert arabic_item.name == "خبز عربي"


@pytest.mark.asyncio
async def test_normalized_name_present_on_every_item():
    """Every item in the response has a non-empty normalized_name."""
    from services.gemini_parser import parse_receipt_images

    raw_json = _load_fixture("lulu_receipt.json")
    mock_response = MagicMock()
    mock_response.text = raw_json

    with patch("services.gemini_parser._call_gemini", new_callable=AsyncMock) as mock_call:
        mock_call.return_value = mock_response
        result = await parse_receipt_images([TEST_IMAGE])

    for item in result.items:
        assert item.normalized_name, f"normalized_name missing on item: {item.name}"


@pytest.mark.asyncio
async def test_total_price_aed_computed_correctly():
    """total_price_aed on each item equals quantity × unit_price_aed."""
    from services.gemini_parser import parse_receipt_images

    raw_json = _load_fixture("lulu_receipt.json")
    mock_response = MagicMock()
    mock_response.text = raw_json

    with patch("services.gemini_parser._call_gemini", new_callable=AsyncMock) as mock_call:
        mock_call.return_value = mock_response
        result = await parse_receipt_images([TEST_IMAGE])

    milk = next(i for i in result.items if "Milk" in i.name)
    assert milk.total_price_aed == Decimal("12.50")
