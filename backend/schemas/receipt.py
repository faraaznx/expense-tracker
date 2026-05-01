from datetime import date
from decimal import Decimal
from typing import Literal, Optional

from pydantic import BaseModel, computed_field


class GeminiItem(BaseModel):
    """A single line item as returned by Gemini."""
    name: str
    normalized_name: str
    quantity: Decimal
    unit_price_aed: Decimal
    category: str

    @computed_field
    @property
    def total_price_aed(self) -> Decimal:
        return self.quantity * self.unit_price_aed


class GeminiRawResponse(BaseModel):
    """Direct Pydantic mapping of Gemini's JSON output."""
    store_name: str
    date: date
    total_aed: Decimal
    source: Literal["physical_photo", "online_screenshot"]
    items: list[GeminiItem]


class GeminiDraftResponse(BaseModel):
    """Response from POST /api/receipts/parse — draft, not yet saved."""
    temp_image_paths: list[str]
    store_name: str
    date: date
    total_aed: Decimal
    source: Literal["physical_photo", "online_screenshot"]
    items: list[GeminiItem]
    item_sum_aed: Decimal
    mismatch_aed: Optional[Decimal]


class ConfirmItemRequest(BaseModel):
    """One line item in the confirm request body (after user review)."""
    name: str
    normalized_name: str
    quantity: Decimal
    unit_price_aed: Decimal
    category: str


class ConfirmReceiptRequest(BaseModel):
    """Body for POST /api/receipts — confirmed and ready to save."""
    temp_image_paths: list[str]
    store_name: str
    date: date
    total_aed: Decimal
    source: Literal["physical_photo", "online_screenshot", "manual"]
    items: list[ConfirmItemRequest]


class LineItemResponse(BaseModel):
    """Line item as returned in receipt responses."""
    id: str
    name: str
    normalized_name: str
    quantity: Decimal
    unit_price_aed: Decimal
    category: str

    @computed_field
    @property
    def total_price_aed(self) -> Decimal:
        return self.quantity * self.unit_price_aed


class ReceiptImageResponse(BaseModel):
    display_order: int
    signed_url: str


class ReceiptResponse(BaseModel):
    """Full receipt detail with line items and signed image URLs."""
    id: str
    store_name: str
    date: date
    total_aed: Decimal
    source: str
    created_at: str
    items: list[LineItemResponse]
    images: list[ReceiptImageResponse]


class ReceiptListItem(BaseModel):
    """Receipt summary for the list view."""
    id: str
    store_name: str
    date: date
    total_aed: Decimal
    source: str
    created_at: str
    item_count: int
