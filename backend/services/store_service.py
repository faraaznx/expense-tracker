from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.receipt import ReceiptSource
from models.store import Store, StoreType


async def upsert_store(db: AsyncSession, name: str, source: str) -> Store:
    """Return existing store by name (case-insensitive) or create a new one.

    Args:
        db: Active async database session.
        name: Store name as extracted by Gemini.
        source: Receipt source string used to infer store type.

    Returns:
        The matched or newly created Store ORM instance.
    """
    result = await db.execute(
        select(Store).where(Store.name.ilike(name))
    )
    existing = result.scalar_one_or_none()
    if existing:
        return existing

    store_type = (
        StoreType.online
        if source == ReceiptSource.online_screenshot
        else StoreType.physical
    )
    store = Store(name=name, type=store_type)
    db.add(store)
    await db.flush()
    return store
