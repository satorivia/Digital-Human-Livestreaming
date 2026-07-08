from hashlib import sha256
from uuid import uuid4

from event_schema import PlatformEvent, PlatformEventType

from app.services.store import InMemoryStore


class MockPlatformAdapter:
    def __init__(self, store: InMemoryStore) -> None:
        self.store = store

    def live_started(self, live_session_id: str) -> PlatformEvent:
        return self._append_event(
            PlatformEvent(
                event_id=str(uuid4()),
                event_type=PlatformEventType.LIVE_STARTED,
                live_session_id=live_session_id,
                raw_payload_hash=self._hash_payload(f"live_started:{live_session_id}"),
            ),
        )

    def comment(self, live_session_id: str, content: str, user: str = "观众") -> PlatformEvent:
        return self._append_event(
            PlatformEvent(
                event_id=str(uuid4()),
                event_type=PlatformEventType.COMMENT_RECEIVED,
                live_session_id=live_session_id,
                user_id_hash=self._hash_payload(user),
                user_nickname=user,
                content=content,
                raw_payload_hash=self._hash_payload(content),
            ),
        )

    def order_created(self, live_session_id: str, order_id: str) -> PlatformEvent:
        return self._append_event(
            PlatformEvent(
                event_id=str(uuid4()),
                event_type=PlatformEventType.ORDER_CREATED,
                live_session_id=live_session_id,
                raw_payload_hash=self._hash_payload(order_id),
                payload={"order_id_hash": self._hash_payload(order_id)},
            ),
        )

    def platform_warning(self, live_session_id: str, message: str) -> PlatformEvent:
        return self._append_event(
            PlatformEvent(
                event_id=str(uuid4()),
                event_type=PlatformEventType.PLATFORM_WARNING_RECEIVED,
                live_session_id=live_session_id,
                content=message,
                raw_payload_hash=self._hash_payload(message),
            ),
        )

    def _append_event(self, event: PlatformEvent) -> PlatformEvent:
        self.store.events.append(event)
        return event

    @staticmethod
    def _hash_payload(payload: str) -> str:
        return sha256(payload.encode("utf-8")).hexdigest()
