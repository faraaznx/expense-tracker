import uuid

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import get_current_user, get_db
from schemas.receipt import (
    ConfirmReceiptRequest,
    GeminiDraftResponse,
    ReceiptListItem,
    ReceiptResponse,
)
from services import receipt_service

router = APIRouter(prefix="/api/receipts", tags=["receipts"])


@router.post("/parse", response_model=GeminiDraftResponse)
async def parse_receipt(
    files: list[UploadFile] = File(...),
    user_id: str = Depends(get_current_user),
):
    """Upload 1–5 receipt images and return parsed draft JSON. Nothing is saved to DB."""
    return await receipt_service.parse_receipt(files, user_id)


@router.post("", response_model=ReceiptResponse, status_code=201)
async def confirm_receipt(
    request: ConfirmReceiptRequest,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Save a confirmed receipt with line items. Moves images from temp to permanent storage."""
    return await receipt_service.confirm_receipt(request, db, user_id)


@router.get("", response_model=list[ReceiptListItem])
async def list_receipts(
    page: int = 1,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List the authenticated user's receipts, newest first."""
    return await receipt_service.list_receipts(db, user_id, page=page)


@router.get("/{receipt_id}", response_model=ReceiptResponse)
async def get_receipt(
    receipt_id: uuid.UUID,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a receipt with all line items and signed image URLs."""
    return await receipt_service.get_receipt_by_id(db, receipt_id, user_id)


@router.delete("/{receipt_id}", status_code=204)
async def delete_receipt(
    receipt_id: uuid.UUID,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a receipt. Cascades to line items, images, and price_history rows."""
    await receipt_service.delete_receipt(db, receipt_id, user_id)
    return None
