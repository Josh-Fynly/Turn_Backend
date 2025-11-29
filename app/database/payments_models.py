# app/database/payments_models.py
from typing import Optional, List
from datetime import datetime
from sqlalchemy import Index, JSON, String, Integer, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base
from app.utils.time import utc_now


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    reference: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)  # amount in kobo/cents
    currency: Mapped[Optional[str]] = mapped_column(String(10), default="NGN")
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending", index=True)
    gateway_response: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False, index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False, index=True
    )

    user = relationship("User", backref="transactions", lazy="joined")

    __table_args__ = (
        Index("idx_transaction_reference_status", "reference", "status"),
        Index("idx_transaction_user_status", "user_id", "status"),
    )


class SubscriptionPlan(Base):
    """
    Defines available plans. Keep this simple and editable by admin.
    """

    __tablename__ = "subscription_plans"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)  # e.g. "monthly_basic"
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    price: Mapped[int] = mapped_column(Integer, nullable=False)  # in whole currency unit (e.g., NGN)
    currency: Mapped[Optional[str]] = mapped_column(String(10), default="NGN")
    interval: Mapped[str] = mapped_column(String(16), default="monthly")  # monthly, yearly
    paystack_plan_code: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)  # if mapped to paystack plan
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False, index=True)


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    plan_id: Mapped[Optional[int]] = mapped_column(ForeignKey("subscription_plans.id", ondelete="SET NULL"), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="inactive", index=True)  # active, inactive, cancelled
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    ends_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    auto_renew: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    extra: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # use 'extra' (avoid Base.metadata name clash)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False, index=True)

    user = relationship("User", back_populates="subscriptions", lazy="joined")
    plan = relationship("SubscriptionPlan", lazy="joined")

    __table_args__ = (
        Index("idx_subscription_user_status", "user_id", "status"),
        Index("idx_subscription_plan_status", "plan_id", "status"),
    )