from event_schema import PlatformEvent, PlatformEventType

from app.services.entities import CommentTask
from app.services.store import InMemoryStore


class CommentRouter:
    blacklisted_fragments = ("拉黑", "spam")
    price_keywords = ("多少钱", "价格", "几块")

    def __init__(self, store: InMemoryStore) -> None:
        self.store = store
        self.seen_event_ids: set[str] = set()

    def route(self, event: PlatformEvent) -> CommentTask | None:
        if event.event_type not in {
            PlatformEventType.COMMENT_RECEIVED,
            PlatformEventType.MANUAL_COMMENT_ENTERED,
        }:
            return None
        if event.event_id in self.seen_event_ids:
            return None
        if any(fragment in (event.content or "") for fragment in self.blacklisted_fragments):
            return None

        self.seen_event_ids.add(event.event_id)
        session = self.store.sessions[event.live_session_id]
        task = CommentTask(
            event_id=event.event_id,
            content=event.content or "",
            product_id=session.product_id,
            intent=self._classify_intent(event.content or ""),
        )
        self.store.comments[task.id] = task
        return task

    def _classify_intent(self, content: str) -> str:
        if any(keyword in content for keyword in self.price_keywords):
            return "price"
        return "product_qa"
