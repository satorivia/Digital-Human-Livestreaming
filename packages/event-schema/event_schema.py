from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
import json

class PlatformEventType(StrEnum):
    LIVE_STARTED='live_started'; LIVE_ENDED='live_ended'; COMMENT_RECEIVED='comment_received'; MANUAL_COMMENT_ENTERED='manual_comment_entered'; ORDER_CREATED='order_created'; PLATFORM_WARNING_RECEIVED='platform_warning_received'

@dataclass
class PlatformEvent:
    event_id: str
    event_type: PlatformEventType
    live_session_id: str
    platform: str = 'mock'
    user_id_hash: str | None = None
    user_nickname: str | None = None
    content: str | None = None
    raw_payload_hash: str | None = None
    payload: dict[str, Any] = field(default_factory=dict)
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    def model_dump(self): return asdict(self)
    def to_json(self) -> str:
        return json.dumps(asdict(self), default=str, ensure_ascii=False)
