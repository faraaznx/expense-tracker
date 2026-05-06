import asyncio

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from supabase import create_client

from config import settings
from database import AsyncSessionLocal

security = HTTPBearer(auto_error=False)

_supabase_client = create_client(settings.supabase_url, settings.supabase_anon_key)


async def get_db():
    """Provide an async database session, committing on success."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """Verify Supabase JWT and return user_id string.

    Raises:
        HTTPException 401: If no token provided or token is invalid/expired.
        HTTPException 503: If the Supabase auth service is unreachable.
    """
    if credentials is None:
        raise HTTPException(status_code=401, detail="Authorization header required")
    token = credentials.credentials
    try:
        user_response = await asyncio.to_thread(_supabase_client.auth.get_user, token)
        return str(user_response.user.id)
    except Exception as e:
        err = str(e).lower()
        if any(k in err for k in ("invalid", "expired", "not found", "jwt", "unauthorized")):
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        raise HTTPException(status_code=503, detail="Auth service temporarily unavailable")
