"""add main mock flow tables"""

import sqlalchemy as sa
from alembic import op

revision = "0004_main_flow_tables"
down_revision = "0003_platform_product_mapping"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "product_selling_point",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("product_id", sa.String(), nullable=False, index=True),
        sa.Column("text", sa.Text(), nullable=False),
    )
    op.create_table(
        "product_forbidden_claim",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("product_id", sa.String(), nullable=False, index=True),
        sa.Column("text", sa.Text(), nullable=False),
    )
    op.create_table(
        "knowledge_chunk",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("product_id", sa.String(), nullable=False, index=True),
        sa.Column("source_type", sa.String(length=80), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
    )
    op.create_table(
        "comment_task",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("event_id", sa.String(), nullable=False, index=True),
        sa.Column("product_id", sa.String(), nullable=False, index=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("intent", sa.String(length=80), nullable=False),
        sa.Column("status", sa.String(length=80), nullable=False),
    )
    op.create_table(
        "answer_candidate",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("comment_task_id", sa.String(), nullable=False, index=True),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("risk", sa.String(length=40)),
        sa.Column("status", sa.String(length=80), nullable=False),
        sa.Column("need_human_review", sa.String(length=10), nullable=False),
    )
    op.create_table(
        "compliance_result",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("candidate_id", sa.String(), nullable=False, index=True),
        sa.Column("risk", sa.String(length=40), nullable=False),
        sa.Column("need_human_review", sa.String(length=10), nullable=False),
        sa.Column("matched_rules", sa.Text(), nullable=False),
    )
    op.create_table(
        "human_review_task",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("candidate_id", sa.String(), nullable=False, index=True),
        sa.Column("status", sa.String(length=80), nullable=False),
        sa.Column("final_text", sa.Text()),
        sa.Column("reviewer_id", sa.String(length=200)),
        sa.Column("reason", sa.Text()),
    )
    op.create_table(
        "speech_task",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("candidate_id", sa.String(), index=True),
        sa.Column("review_id", sa.String(), index=True),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("audio_url", sa.Text()),
        sa.Column("priority", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=80), nullable=False),
        sa.Column("failure_reason", sa.Text()),
    )
    op.create_table(
        "tts_asset",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("cache_key", sa.String(length=128), nullable=False, unique=True),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("audio_url", sa.Text(), nullable=False),
        sa.Column("provider", sa.String(length=80), nullable=False),
        sa.Column("duration_ms", sa.Integer(), nullable=False),
    )
    op.create_table(
        "avatar_command_log",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("speech_id", sa.String(), index=True),
        sa.Column("command", sa.String(length=80), nullable=False),
        sa.Column("status", sa.String(length=80), nullable=False),
        sa.Column("message", sa.Text()),
    )
    op.create_table(
        "audit_log",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("entity_type", sa.String(length=120), nullable=False),
        sa.Column("entity_id", sa.String(), nullable=False, index=True),
        sa.Column("action", sa.String(length=120), nullable=False),
        sa.Column("actor_id", sa.String(length=200)),
        sa.Column("metadata_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    for table_name in [
        "audit_log",
        "avatar_command_log",
        "tts_asset",
        "speech_task",
        "human_review_task",
        "compliance_result",
        "answer_candidate",
        "comment_task",
        "knowledge_chunk",
        "product_forbidden_claim",
        "product_selling_point",
    ]:
        op.drop_table(table_name)
