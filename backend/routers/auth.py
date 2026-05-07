import asyncio
import logging

from fastapi import APIRouter, Depends, HTTPException
from supabase import create_client

from config import settings
from dependencies import get_current_user
from schemas.auth import AuthResponse, LoginRequest, SignUpRequest

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["auth"])

_supabase_client = create_client(settings.supabase_url, settings.supabase_anon_key)


@router.post("/signup", response_model=AuthResponse)
async def signup(request: SignUpRequest):
    """Register a new user with email and password.

    Returns 202 if email confirmation is required before the account is active.
    """
    try:
        response = await asyncio.to_thread(
            _supabase_client.auth.sign_up,
            {"email": request.email, "password": request.password},
        )
        if response.session is None:
            raise HTTPException(
                status_code=202,
                detail="Account created. Please confirm your email before logging in.",
            )
        return AuthResponse(
            access_token=response.session.access_token,
            user_id=str(response.user.id),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Supabase signup error: %s", e)
        raise HTTPException(status_code=400, detail="Signup failed. Email may already be in use.")


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """Authenticate with email and password."""
    try:
        response = await asyncio.to_thread(
            _supabase_client.auth.sign_in_with_password,
            {"email": request.email, "password": request.password},
        )
        return AuthResponse(
            access_token=response.session.access_token,
            user_id=str(response.user.id),
        )
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid email or password")


@router.post("/logout", status_code=204)
async def logout(user_id: str = Depends(get_current_user)):
    """Logout — client must discard the JWT."""
    return None
