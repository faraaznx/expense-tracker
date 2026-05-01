from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import get_current_user, get_db
from models.store import Store
from schemas.store import StoreResponse

router = APIRouter(prefix="/api/stores", tags=["stores"])


@router.get("", response_model=list[StoreResponse])
async def list_stores(
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all known stores."""
    result = await db.execute(select(Store).order_by(Store.name))
    stores = result.scalars().all()
    return [
        StoreResponse(id=str(s.id), name=s.name, type=s.type.value, logo_url=s.logo_url)
        for s in stores
    ]
