import uuid
from decimal import Decimal

import pytest

TEST_USER_ID = "550e8400-e29b-41d4-a716-446655440000"

CONFIRM_PAYLOAD = {
    "temp_image_paths": [f"receipts/temp/{TEST_USER_ID}/abc123.jpg"],
    "store_name": "Lulu Hypermarket",
    "date": "2026-04-28",
    "total_aed": "25.00",
    "source": "physical_photo",
    "items": [
        {
            "name": "Lacnor Full Cream Milk 1L",
            "normalized_name": "Full Cream Milk 1L",
            "quantity": "2",
            "unit_price_aed": "6.25",
            "category": "Dairy & Eggs",
        },
        {
            "name": "Tomatoes 1kg",
            "normalized_name": "Tomatoes 1kg",
            "quantity": "1",
            "unit_price_aed": "10.50",
            "category": "Produce",
        },
    ],
}


@pytest.fixture
def mock_storage(monkeypatch):
    deleted_paths = []

    async def mock_move(from_path, to_path):
        return to_path

    async def mock_signed_url(path, expires_in=3600):
        return f"https://supabase.test/signed/{path}"

    async def mock_delete(path):
        deleted_paths.append(path)

    monkeypatch.setattr("utils.supabase_storage.move_file", mock_move)
    monkeypatch.setattr("utils.supabase_storage.get_signed_url", mock_signed_url)
    monkeypatch.setattr("utils.supabase_storage.delete_file", mock_delete)
    return deleted_paths


@pytest.mark.asyncio
async def test_confirm_creates_receipt_and_line_items(client, mock_storage):
    """POST /api/receipts saves a receipt with line items and returns it."""
    response = await client.post("/api/receipts", json=CONFIRM_PAYLOAD)
    assert response.status_code == 201
    body = response.json()
    assert body["store_name"] == "Lulu Hypermarket"
    assert len(body["items"]) == 2
    assert body["items"][0]["total_price_aed"] == "12.50"


@pytest.mark.asyncio
async def test_confirm_auto_creates_new_store(client, mock_storage):
    """A new store name creates a Store row on the fly."""
    payload = {**CONFIRM_PAYLOAD, "store_name": "Brand New Store XYZ"}
    response = await client.post("/api/receipts", json=payload)
    assert response.status_code == 201
    assert response.json()["store_name"] == "Brand New Store XYZ"


@pytest.mark.asyncio
async def test_confirm_reuses_existing_store(client, mock_storage):
    """Confirming two receipts at the same store reuses the existing Store row."""
    await client.post("/api/receipts", json=CONFIRM_PAYLOAD)
    await client.post("/api/receipts", json=CONFIRM_PAYLOAD)

    response = await client.get("/api/stores")
    stores = response.json()
    lulu_stores = [s for s in stores if s["name"] == "Lulu Hypermarket"]
    assert len(lulu_stores) == 1


@pytest.mark.asyncio
async def test_total_price_aed_computed_correctly(client, mock_storage):
    """total_price_aed = quantity × unit_price_aed, computed server-side."""
    response = await client.post("/api/receipts", json=CONFIRM_PAYLOAD)
    body = response.json()
    milk = next(i for i in body["items"] if "Milk" in i["name"])
    assert Decimal(milk["total_price_aed"]) == Decimal("12.50")


@pytest.mark.asyncio
async def test_get_receipts_returns_list(client, mock_storage):
    """GET /api/receipts returns receipts for the authenticated user."""
    await client.post("/api/receipts", json=CONFIRM_PAYLOAD)
    response = await client.get("/api/receipts")
    assert response.status_code == 200
    assert len(response.json()) >= 1


@pytest.mark.asyncio
async def test_get_receipt_by_id_returns_signed_urls(client, mock_storage):
    """GET /api/receipts/{id} returns signed image URLs."""
    create_response = await client.post("/api/receipts", json=CONFIRM_PAYLOAD)
    receipt_id = create_response.json()["id"]

    response = await client.get(f"/api/receipts/{receipt_id}")
    assert response.status_code == 200
    body = response.json()
    assert len(body["images"]) == 1
    assert "signed" in body["images"][0]["signed_url"]


@pytest.mark.asyncio
async def test_delete_receipt_removes_storage_files(client, mock_storage):
    """DELETE /api/receipts/{id} calls delete_file for every stored image."""
    deleted_paths = mock_storage
    create_response = await client.post("/api/receipts", json=CONFIRM_PAYLOAD)
    receipt_id = create_response.json()["id"]

    response = await client.delete(f"/api/receipts/{receipt_id}")
    assert response.status_code == 204
    assert len(deleted_paths) == 1


@pytest.mark.asyncio
async def test_confirm_rejects_path_not_owned_by_user(client, mock_storage):
    """Confirm with a temp path belonging to another user returns 403."""
    payload = {
        **CONFIRM_PAYLOAD,
        "temp_image_paths": ["receipts/temp/other-user-id/abc123.jpg"],
    }
    response = await client.post("/api/receipts", json=payload)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_confirm_requires_auth(unauthenticated_client, mock_storage):
    """POST /api/receipts returns 401 when no Authorization header is sent."""
    response = await unauthenticated_client.post("/api/receipts", json=CONFIRM_PAYLOAD)
    assert response.status_code == 401
