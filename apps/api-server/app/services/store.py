from event_schema import PlatformEvent

from app.services.entities import (
    AnswerCandidate,
    CommentTask,
    HumanReviewTask,
    LiveSession,
    Product,
    SpeechTask,
    TTSAsset,
)


class InMemoryStore:
    """Test-only persistence boundary used by Mock providers.

    The service APIs are intentionally persistence-agnostic so this store can be replaced
    by SQLAlchemy repositories without changing business orchestration tests.
    """

    def __init__(self) -> None:
        self.products: dict[str, Product] = {}
        self.sessions: dict[str, LiveSession] = {}
        self.events: list[PlatformEvent] = []
        self.state_logs: list[dict[str, object]] = []
        self.comments: dict[str, CommentTask] = {}
        self.candidates: dict[str, AnswerCandidate] = {}
        self.reviews: dict[str, HumanReviewTask] = {}
        self.speeches: dict[str, SpeechTask] = {}
        self.audit_logs: list[dict[str, object]] = []
        self.avatar_logs: list[dict[str, object]] = []
        self.llm_logs: list[dict[str, object]] = []
        self.tts_assets: dict[str, TTSAsset] = {}
        self.knowledge: list[tuple[str, str]] = []
