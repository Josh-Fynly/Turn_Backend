
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
        "transactions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("reference", sa.String(length=128), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("currency", sa.String(length=10), server_default="NGN"),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("gateway_response", sa.Text(), nullable=True),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.UniqueConstraint("reference"),
    )

    op.create_index(
        "idx_transaction_reference_status",
        "transactions",
        ["reference", "status"],
    )

    op.create_index(
        "idx_transaction_user_status",
        "transactions",
        ["user_id", "status"],
    )

    op.create_table(
        "subscriptions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("plan_id", sa.String(length=64), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ends_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("auto_renew", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )

    op.create_index(
        "idx_subscription_user_status",
        "subscriptions",
        ["user_id", "status"],
    )

    op.create_index(
        "idx_subscription_plan_status",
        "subscriptions",
        ["plan_id", "status"],
    )


def downgrade() -> None:
    op.drop_index("idx_subscription_plan_status", table_name="subscriptions")
    op.drop_index("idx_subscription_user_status", table_name="subscriptions")
    op.drop_table("subscriptions")

    op.drop_index("idx_transaction_user_status", table_name="transactions")
    op.drop_index("idx_transaction_reference_status", table_name="transactions")
    op.drop_table("transactions")