from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from dependencies import get_current_user
from routers import auth

app = FastAPI(title="UAE Expense Tracker")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)


@app.get("/health")
async def health():
    return {"status": "ok"}


# Temporary stub — replaced in Task 8
@app.get("/api/receipts")
async def receipts_stub(user_id: str = Depends(get_current_user)):
    return []
