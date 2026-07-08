"""add platform product mapping"""

import sqlalchemy as sa
from alembic import op

revision = "0003_platform_product_mapping"
down_revision = "0002_voice_profiles"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "platform_product_mapping",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("platform", sa.String(length=80), nullable=False, index=True),
        sa.Column("platform_product_id", sa.String(length=200), nullable=False, index=True),
        sa.Column("product_id", sa.String(), nullable=False, index=True),
    )


def downgrade() -> None:
    op.drop_table("platform_product_mapping")
