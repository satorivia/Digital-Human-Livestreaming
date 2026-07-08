from pathlib import Path

MIGRATION = Path("apps/api-server/alembic/versions/0004_main_flow_tables.py")
REPOSITORY = Path("apps/api-server/app/repositories/main_flow.py")


def test_main_flow_migration_declares_required_tables() -> None:
    migration = MIGRATION.read_text(encoding="utf-8")

    for table_name in [
        "product_selling_point",
        "product_forbidden_claim",
        "knowledge_chunk",
        "comment_task",
        "answer_candidate",
        "compliance_result",
        "human_review_task",
        "speech_task",
        "tts_asset",
        "avatar_command_log",
        "audit_log",
    ]:
        assert f'"{table_name}"' in migration


def test_repository_layer_declares_p0_boundaries() -> None:
    repository = REPOSITORY.read_text(encoding="utf-8")

    for class_name in [
        "ProductRepository",
        "LiveSessionRepository",
        "CommentTaskRepository",
        "AnswerCandidateRepository",
        "HumanReviewTaskRepository",
        "SpeechTaskRepository",
        "ComplianceResultRepository",
        "KnowledgeChunkRepository",
        "TTSAssetRepository",
        "AvatarCommandLogRepository",
        "AuditLogRepository",
    ]:
        assert f"class {class_name}" in repository
