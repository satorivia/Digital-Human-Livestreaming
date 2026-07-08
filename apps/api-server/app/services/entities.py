from dataclasses import dataclass, field
from enum import StrEnum
from uuid import uuid4


class LiveState(StrEnum):
    CREATED = "created"
    LIVE = "live"
    WAITING_REVIEW = "waiting_review"
    SPEAKING = "speaking"
    HUMAN_TAKEOVER = "human_takeover"
    ENDED = "ended"


class Risk(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    BLOCKED = "blocked"


class CandidateStatus(StrEnum):
    GENERATED = "generated"
    NEEDS_HUMAN_REVIEW = "needs_human_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    BLOCKED = "blocked"


class ReviewStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class SpeechStatus(StrEnum):
    QUEUED = "queued"
    SPEAKING = "speaking"
    FINISHED = "finished"
    INTERRUPTED = "interrupted"
    FAILED = "failed"


class AvatarCommandStatus(StrEnum):
    SUCCESS = "success"
    FAILED = "failed"


@dataclass(slots=True)
class SKU:
    name: str
    price_cents: int
    stock: int
    id: str = field(default_factory=lambda: str(uuid4()))


@dataclass(slots=True)
class Product:
    title: str
    id: str = field(default_factory=lambda: str(uuid4()))
    skus: list[SKU] = field(default_factory=list)
    faqs: dict[str, str] = field(default_factory=dict)
    selling_points: list[str] = field(default_factory=list)
    forbidden: list[str] = field(default_factory=list)


@dataclass(slots=True)
class LiveSession:
    product_id: str
    id: str = field(default_factory=lambda: str(uuid4()))
    state: LiveState = LiveState.CREATED


@dataclass(slots=True)
class CommentTask:
    event_id: str
    content: str
    product_id: str
    intent: str
    status: str = "pending"
    id: str = field(default_factory=lambda: str(uuid4()))


@dataclass(slots=True)
class AnswerCandidate:
    comment_task_id: str
    text: str
    risk: Risk | None = None
    status: CandidateStatus = CandidateStatus.GENERATED
    id: str = field(default_factory=lambda: str(uuid4()))
    need_human_review: bool = True
    matched_rules: list[str] = field(default_factory=list)


@dataclass(slots=True)
class HumanReviewTask:
    candidate_id: str
    status: ReviewStatus = ReviewStatus.PENDING
    final_text: str | None = None
    reviewer_id: str | None = None
    reason: str | None = None
    id: str = field(default_factory=lambda: str(uuid4()))


@dataclass(slots=True)
class SpeechTask:
    text: str
    audio_url: str | None = None
    priority: int = 100
    status: SpeechStatus = SpeechStatus.QUEUED
    candidate_id: str | None = None
    review_id: str | None = None
    failure_reason: str | None = None
    id: str = field(default_factory=lambda: str(uuid4()))


@dataclass(slots=True)
class TTSAsset:
    cache_key: str
    text: str
    audio_url: str
    provider: str
    duration_ms: int
    id: str = field(default_factory=lambda: str(uuid4()))


@dataclass(slots=True)
class VoiceProfile:
    name: str
    provider: str
    voice_id: str
    id: str = field(default_factory=lambda: str(uuid4()))


@dataclass(slots=True)
class VoiceLicense:
    voice_profile_id: str
    authorized_by: str
    authorization_record_url: str
    id: str = field(default_factory=lambda: str(uuid4()))
