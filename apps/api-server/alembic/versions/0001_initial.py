"""initial core tables"""

import sqlalchemy as sa
from alembic import op

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "merchant",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("name", sa.String(length=200), nullable=False),
    )
    op.create_table(
        "app_user",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("email", sa.String(length=320), nullable=False, unique=True),
    )
    op.create_table(
        "product",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("title", sa.String(length=300), nullable=False),
    )
    op.create_table(
        "sku",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("product_id", sa.String(), nullable=False, index=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("price_cents", sa.Integer(), nullable=False),
        sa.Column("stock", sa.Integer(), nullable=False),
    )
    op.create_table(
        "product_faq",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("product_id", sa.String(), nullable=False, index=True),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("answer", sa.Text(), nullable=False),
    )
    op.create_table(
        "live_session",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("product_id", sa.String(), nullable=False),
        sa.Column("state", sa.String(length=80), nullable=False),
    )
    op.create_table(
        "live_state_log",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("session_id", sa.String(), nullable=False),
        sa.Column("from_state", sa.String(length=80)),
        sa.Column("to_state", sa.String(length=80), nullable=False),
    )
    op.create_table(
        "platform_event_log",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("event_type", sa.String(length=120), nullable=False),
        sa.Column("raw_payload_hash", sa.String(length=128)),
    )


def downgrade() -> None:
    for table_name in [
        "platform_event_log",
        "live_state_log",
        "live_session",
        "product_faq",
        "sku",
        "product",
        "app_user",
        "merchant",
    ]:
        op.drop_table(table_name)
