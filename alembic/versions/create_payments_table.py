
"""create payments table

Revision ID: manual_create_payments
Revises: 
Create Date: 2025-01-01
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "manual_create_payments"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "payments",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, nullable=False),
        sa.Column("reference", sa.String(length=100), unique=True, nullable=False),
        sa.Column("amount", sa.Integer, nullable=False),  # stored in kobo
        sa.Column("currency", sa.String(length=10), server_default="NGN"),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("provider", sa.String(length=30), server_default="paystack"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("payments")