from typing import Optional
from datetime import datetime
from sqlalchemy import Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String, Integer, Boolean, DateTime, Text
from app.database.base import Base  # adjust import path to your Base
from app.utils.time import utc_now  # adjust if you use a different util

class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    reference: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)  # stored in kobo/cents
    currency: Mapped[Optional[str]] = mapped_column(String(10), default="NGN")
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending", index=True)
    gateway_response: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False, index=True)

    user = relationship("User", backref="transactions")

    __table_args__ = (
        Index("idx_transaction_reference_status", "reference", "status"),
        Index("idx_transaction_user_status", "user_id", "status"),
    )


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    plan_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)  # your product/plan reference
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="inactive", index=True)  # active, inactive, cancelled
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    ends_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    auto_renew: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False, index=True)

    user = relationship("User", back_populates="subscriptions")

    __table_args__ = (
        Index("idx_subscription_user_status", "user_id", "status"),
        Index("idx_subscription_plan_status", "plan_id", "status"),
    )

# Add back-populates in User model (update user_models.py)
# after the User class add:
# subscriptions: Mapped[List["Subscription"]] = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")