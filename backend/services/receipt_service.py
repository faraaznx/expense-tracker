import uuid
from decimal import Decimal

from fastapi import HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.line_item import LineItem
from models.price_history import PriceHistory
from models.receipt import Receipt
from models.receipt_image import ReceiptImage
from schemas.receipt import (
    ConfirmReceiptRequest,
    GeminiDraftResponse,
    LineItemResponse,
    ReceiptImageResponse,
    ReceiptListItem,
    ReceiptResponse,
)
from services import gemini_parser
from services.store_service import upsert_store
from utils import supabase_storage


async def parse_receipt(
    files: list[UploadFile],
    user_id: str,
) -> GeminiDraftResponse:
    """Upload images to temp storage, parse with Gemini, return draft.

    Args:
        files: List of uploaded image files (1–5).
        user_id: Authenticated user's UUID string.

    Returns:
        GeminiDraftResponse with temp_image_paths set.

    Raises:
        HTTPException 400: If more than 5 files are uploaded.
    """
    if len(files) > 5:
        raise HTTPException(status_code=400, detail="Maximum 5 images per receipt.")

    image_bytes_list = [await f.read() for f in files]

    temp_paths: list[str] = []
    for img_bytes in image_bytes_list:
        path = f"receipts/temp/{user_id}/{uuid.uuid4()}.jpg"
        await supabase_storage.upload_file(path, img_bytes)
        temp_paths.append(path)

    draft = await gemini_parser.parse_receipt_images(image_bytes_list)
    return draft.model_copy(update={"temp_image_paths": temp_paths})


async def confirm_receipt(
    request: ConfirmReceiptRequest,
    db: AsyncSession,
    user_id: str,
) -> ReceiptResponse:
    """Save a confirmed receipt, move images to permanent storage, write price history.

    Args:
        request: Confirmed receipt data from the frontend review screen.
        db: Active async database session.
        user_id: Authenticated user's UUID string.

    Returns:
        ReceiptResponse with full line items and signed image URLs.

    Raises:
        HTTPException 403: If any temp path does not belong to this user.
    """
    expected_prefix = f"receipts/temp/{user_id}/"
    for path in request.temp_image_paths:
        if not path.startswith(expected_prefix):
            raise HTTPException(status_code=403, detail="Invalid image path.")

    path_pairs = [
        (temp, f"receipts/{user_id}/{uuid.uuid4()}/{i}.jpg")
        for i, temp in enumerate(request.temp_image_paths)
    ]

    store = await upsert_store(db, request.store_name, request.source)

    receipt = Receipt(
        user_id=uuid.UUID(user_id),
        store_id=store.id,
        date=request.date,
        total_aed=Decimal(str(request.total_aed)),
        source=request.source,
    )
    db.add(receipt)
    await db.flush()

    for i, (_, perm_path) in enumerate(path_pairs):
        db.add(ReceiptImage(
            receipt_id=receipt.id,
            storage_path=perm_path,
            display_order=i,
        ))

    for item in request.items:
        db.add(LineItem(
            receipt_id=receipt.id,
            name=item.name,
            normalized_name=item.normalized_name,
            quantity=Decimal(str(item.quantity)),
            unit_price_aed=Decimal(str(item.unit_price_aed)),
            category=item.category,
        ))
        db.add(PriceHistory(
            user_id=uuid.UUID(user_id),
            normalized_name=item.normalized_name,
            store_id=store.id,
            price_aed=Decimal(str(item.unit_price_aed)),
            date=request.date,
            receipt_id=receipt.id,
        ))

    await db.flush()

    for temp_path, perm_path in path_pairs:
        await supabase_storage.move_file(temp_path, perm_path)

    return await get_receipt_by_id(db, receipt.id, user_id)


async def get_receipt_by_id(
    db: AsyncSession, receipt_id: uuid.UUID, user_id: str
) -> ReceiptResponse:
    """Fetch a receipt with line items and fresh signed image URLs.

    Args:
        db: Active async database session.
        receipt_id: UUID of the receipt to fetch.
        user_id: Must match receipt.user_id — enforces ownership.

    Returns:
        ReceiptResponse.

    Raises:
        HTTPException 404: If receipt not found or doesn't belong to user.
    """
    result = await db.execute(
        select(Receipt)
        .options(
            selectinload(Receipt.store),
            selectinload(Receipt.line_items),
            selectinload(Receipt.images),
        )
        .where(Receipt.id == receipt_id, Receipt.user_id == uuid.UUID(user_id))
    )
    receipt = result.scalar_one_or_none()
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found.")

    images = []
    for img in sorted(receipt.images, key=lambda x: x.display_order):
        signed_url = await supabase_storage.get_signed_url(img.storage_path)
        images.append(ReceiptImageResponse(
            display_order=img.display_order,
            signed_url=signed_url,
        ))

    return ReceiptResponse(
        id=str(receipt.id),
        store_name=receipt.store.name,
        date=receipt.date,
        total_aed=receipt.total_aed,
        source=receipt.source.value if hasattr(receipt.source, "value") else receipt.source,
        created_at=receipt.created_at.isoformat(),
        items=[
            LineItemResponse(
                id=str(item.id),
                name=item.name,
                normalized_name=item.normalized_name,
                quantity=item.quantity,
                unit_price_aed=item.unit_price_aed,
                category=item.category,
            )
            for item in receipt.line_items
        ],
        images=images,
    )


async def list_receipts(
    db: AsyncSession, user_id: str, page: int = 1, page_size: int = 20
) -> list[ReceiptListItem]:
    """List receipts for a user, newest first, paginated.

    Args:
        db: Active async database session.
        user_id: Authenticated user's UUID string.
        page: 1-based page number.
        page_size: Number of results per page.

    Returns:
        List of ReceiptListItem summaries.
    """
    offset = (page - 1) * page_size
    result = await db.execute(
        select(Receipt)
        .options(selectinload(Receipt.store), selectinload(Receipt.line_items))
        .where(Receipt.user_id == uuid.UUID(user_id))
        .order_by(Receipt.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    receipts = result.scalars().all()
    return [
        ReceiptListItem(
            id=str(r.id),
            store_name=r.store.name,
            date=r.date,
            total_aed=r.total_aed,
            source=r.source.value if hasattr(r.source, "value") else r.source,
            created_at=r.created_at.isoformat(),
            item_count=len(r.line_items),
        )
        for r in receipts
    ]


async def delete_receipt(
    db: AsyncSession, receipt_id: uuid.UUID, user_id: str
) -> None:
    """Delete a receipt, its storage images, and all DB children.

    Args:
        db: Active async database session.
        receipt_id: UUID of the receipt to delete.
        user_id: Must match receipt.user_id — enforces ownership.

    Raises:
        HTTPException 404: If receipt not found or doesn't belong to user.
    """
    result = await db.execute(
        select(Receipt)
        .options(selectinload(Receipt.images))
        .where(Receipt.id == receipt_id, Receipt.user_id == uuid.UUID(user_id))
    )
    receipt = result.scalar_one_or_none()
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found.")

    storage_paths = [img.storage_path for img in receipt.images]
    await db.delete(receipt)
    await db.flush()

    for path in storage_paths:
        await supabase_storage.delete_file(path)
