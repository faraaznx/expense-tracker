import enum
import uuid
from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from .base import Base


class ReceiptSource(str, enum.Enum):
    physical_photo = "physical_photo"
    online_screenshot = "online_screenshot"
    manual = "manual"


class Receipt(Base):
    __tablename__ = "receipts"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False, index=True)
    store_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("stores.id"), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    total_aed: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    source: Mapped[ReceiptSource] = mapped_column(
        Enum(ReceiptSource, name="receipt_source"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    store = relationship("Store", back_populates="receipts")
    line_items = relationship("LineItem", back_populates="receipt", cascade="all, delete-orphan")
    images = relationship("ReceiptImage", back_populates="receipt", cascade="all, delete-orphan")
