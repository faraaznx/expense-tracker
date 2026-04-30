import asyncio

from fastapi import APIRouter, Depends, HTTPException
from supabase import create_client

from config import settings
from dependencies import get_current_user
from schemas.auth import AuthResponse, LoginRequest, SignUpRequest

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/signup", response_model=AuthResponse)
async def signup(request: SignUpRequest):
    """Register a new user with email and password."""
    client = create_client(settings.supabase_url, settings.supabase_anon_key)
    try:
        response = await asyncio.to_thread(
            client.auth.sign_up,
            {"email": request.email, "password": request.password},
        )
        return AuthResponse(
            access_token=response.session.access_token,
            user_id=str(response.user.id),
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """Authenticate with email and password."""
    client = create_client(settings.supabase_url, settings.supabase_anon_key)
    try:
        response = await asyncio.to_thread(
            client.auth.sign_in_with_password,
            {"email": request.email, "password": request.password},
        )
        return AuthResponse(
            access_token=response.session.access_token,
            user_id=str(response.user.id),
        )
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid email or password")


@router.post("/logout", status_code=204)
async def logout(user_id: str = Depends(get_current_user)):
    """Logout — client must discard the JWT."""
    return None
