import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from .base import Base


class PriceHistory(Base):
    __tablename__ = "price_history"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False, index=True)
    normalized_name: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    store_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("stores.id"), nullable=False
    )
    price_aed: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    receipt_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("receipts.id", ondelete="CASCADE"), nullable=False
    )

    receipt: Mapped["Receipt"] = relationship("Receipt", viewonly=True)
    store: Mapped["Store"] = relationship("Store", back_populates="price_history")
