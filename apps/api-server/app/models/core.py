from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class MerchantModel(Base):
    __tablename__ = "merchant"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)


class AppUserModel(Base):
    __tablename__ = "app_user"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    email: Mapped[str] = mapped_column(String(320), nullable=False, unique=True)


class ProductModel(Base):
    __tablename__ = "product"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    title: Mapped[str] = mapped_column(String(300), nullable=False)


class SkuModel(Base):
    __tablename__ = "sku"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    product_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    price_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    stock: Mapped[int] = mapped_column(Integer, nullable=False)


class ProductFaqModel(Base):
    __tablename__ = "product_faq"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    product_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)


class LiveSessionModel(Base):
    __tablename__ = "live_session"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    product_id: Mapped[str] = mapped_column(String, nullable=False)
    state: Mapped[str] = mapped_column(String(80), nullable=False)


class VoiceProfileModel(Base):
    __tablename__ = "voice_profile"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    provider: Mapped[str] = mapped_column(String(80), nullable=False)
    voice_id: Mapped[str] = mapped_column(String(200), nullable=False)


class VoiceLicenseModel(Base):
    __tablename__ = "voice_license"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    voice_profile_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    authorized_by: Mapped[str] = mapped_column(String(200), nullable=False)
    authorization_record_url: Mapped[str] = mapped_column(Text, nullable=False)


class PlatformProductMappingModel(Base):
    __tablename__ = "platform_product_mapping"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    platform: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    platform_product_id: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    product_id: Mapped[str] = mapped_column(String, nullable=False, index=True)


class ProductSellingPointModel(Base):
    __tablename__ = "product_selling_point"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    product_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)


class ProductForbiddenClaimModel(Base):
    __tablename__ = "product_forbidden_claim"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    product_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)


class KnowledgeChunkModel(Base):
    __tablename__ = "knowledge_chunk"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    product_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    source_type: Mapped[str] = mapped_column(String(80), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)


class CommentTaskModel(Base):
    __tablename__ = "comment_task"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    event_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    product_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    intent: Mapped[str] = mapped_column(String(80), nullable=False)
    status: Mapped[str] = mapped_column(String(80), nullable=False)


class AnswerCandidateModel(Base):
    __tablename__ = "answer_candidate"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    comment_task_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    risk: Mapped[str | None] = mapped_column(String(40))
    status: Mapped[str] = mapped_column(String(80), nullable=False)
    need_human_review: Mapped[str] = mapped_column(String(10), nullable=False, default="true")


class ComplianceResultModel(Base):
    __tablename__ = "compliance_result"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    candidate_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    risk: Mapped[str] = mapped_column(String(40), nullable=False)
    need_human_review: Mapped[str] = mapped_column(String(10), nullable=False)
    matched_rules: Mapped[str] = mapped_column(Text, nullable=False, default="[]")


class HumanReviewTaskModel(Base):
    __tablename__ = "human_review_task"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    candidate_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(80), nullable=False)
    final_text: Mapped[str | None] = mapped_column(Text)
    reviewer_id: Mapped[str | None] = mapped_column(String(200))
    reason: Mapped[str | None] = mapped_column(Text)


class SpeechTaskModel(Base):
    __tablename__ = "speech_task"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    candidate_id: Mapped[str | None] = mapped_column(String, index=True)
    review_id: Mapped[str | None] = mapped_column(String, index=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    audio_url: Mapped[str | None] = mapped_column(Text)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    status: Mapped[str] = mapped_column(String(80), nullable=False)
    failure_reason: Mapped[str | None] = mapped_column(Text)


class TTSAssetModel(Base):
    __tablename__ = "tts_asset"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    cache_key: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    audio_url: Mapped[str] = mapped_column(Text, nullable=False)
    provider: Mapped[str] = mapped_column(String(80), nullable=False)
    duration_ms: Mapped[int] = mapped_column(Integer, nullable=False)


class AvatarCommandLogModel(Base):
    __tablename__ = "avatar_command_log"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    speech_id: Mapped[str | None] = mapped_column(String, index=True)
    command: Mapped[str] = mapped_column(String(80), nullable=False)
    status: Mapped[str] = mapped_column(String(80), nullable=False)
    message: Mapped[str | None] = mapped_column(Text)


class AuditLogModel(Base):
    __tablename__ = "audit_log"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    entity_type: Mapped[str] = mapped_column(String(120), nullable=False)
    entity_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(120), nullable=False)
    actor_id: Mapped[str | None] = mapped_column(String(200))
    metadata_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
