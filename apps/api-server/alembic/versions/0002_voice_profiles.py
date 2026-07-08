"""add voice profiles and licenses"""

import sqlalchemy as sa
from alembic import op

revision = "0002_voice_profiles"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "voice_profile",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("provider", sa.String(length=80), nullable=False),
        sa.Column("voice_id", sa.String(length=200), nullable=False),
    )
    op.create_table(
        "voice_license",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("voice_profile_id", sa.String(), nullable=False, index=True),
        sa.Column("authorized_by", sa.String(length=200), nullable=False),
        sa.Column("authorization_record_url", sa.Text(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("voice_license")
    op.drop_table("voice_profile")
