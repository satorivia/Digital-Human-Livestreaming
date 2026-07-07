from datetime import datetime, timezone
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class PlatformEventType(StrEnum):
    LIVE_STARTED = "live_started"
    LIVE_ENDED = "live_ended"
    COMMENT_RECEIVED = "comment_received"
    MANUAL_COMMENT_ENTERED = "manual_comment_entered"
    ORDER_CREATED = "order_created"
    PLATFORM_WARNING_RECEIVED = "platform_warning_received"


class PlatformEvent(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    event_id: str
    event_type: PlatformEventType
    live_session_id: str
    platform: str = "mock"
    user_id_hash: str | None = None
    user_nickname: str | None = None
    content: str | None = None
    raw_payload_hash: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def to_json(self) -> str:
        return self.model_dump_json()
