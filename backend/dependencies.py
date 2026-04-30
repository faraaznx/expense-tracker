import asyncio

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from supabase import create_client

from config import settings
from database import AsyncSessionLocal

security = HTTPBearer(auto_error=False)


async def get_db():
    """Provide an async database session."""
    async with AsyncSessionLocal() as session:
        yield session


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> str:
    """Verify Supabase JWT and return user_id string.

    Returns the Supabase user ID on success.
    Raises HTTP 401 when the Authorization header is missing or the token is invalid/expired.
    """
    if credentials is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = credentials.credentials
    try:
        client = create_client(settings.supabase_url, settings.supabase_anon_key)
        user_response = await asyncio.to_thread(client.auth.get_user, token)
        return str(user_response.user.id)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
