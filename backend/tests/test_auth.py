from unittest.mock import MagicMock, patch

import pytest


@pytest.mark.asyncio
async def test_protected_endpoint_requires_jwt(unauthenticated_client):
    """Any protected endpoint returns 401 when no Authorization header is sent."""
    response = await unauthenticated_client.get("/api/receipts")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_protected_endpoint_rejects_invalid_jwt(unauthenticated_client):
    """A malformed or expired JWT returns 401."""
    with patch("dependencies._supabase_client") as mock_client:
        mock_client.auth.get_user.side_effect = Exception("invalid JWT")
        response = await unauthenticated_client.get(
            "/api/receipts",
            headers={"Authorization": "Bearer not-a-real-token"},
        )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_protected_endpoint_accepts_valid_jwt(client):
    """An injected valid user_id (via dependency override) gets through."""
    response = await client.get("/api/receipts")
    assert response.status_code == 200
