from hashlib import sha256
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, SecretStr

from event_schema import PlatformEvent, PlatformEventType

from app.core.errors import DomainError
from app.services.store import InMemoryStore


class PlatformType(str):
    TAOBAO = "taobao_live"


class TaobaoLiveAdapterConfig(BaseModel):
    """Conservative config model for Taobao Live integration placeholders.

    This model intentionally stores credentials as SecretStr and is not used to call
    Taobao APIs in automated tests or mock flows.
    """

    app_key: str
    app_secret: SecretStr | None = None
    webhook_secret: SecretStr | None = None
    shop_id: str | None = None
    enabled: bool = False
    sandbox: bool = True


class PlatformProductMapping(BaseModel):
    platform: str
    platform_product_id: str
    product_id: str


class TaobaoLiveAdapter:
    platform = PlatformType.TAOBAO

    def __init__(self, store: InMemoryStore, config: TaobaoLiveAdapterConfig) -> None:
        self.store = store
        self.config = config
        self.product_mappings: dict[str, PlatformProductMapping] = {}

    def verify_signature_placeholder(self, raw_payload: str, signature: str | None) -> bool:
        """Placeholder for official Taobao webhook signature verification.

        The MVP does not implement real verification because no real platform webhook is
        connected. Missing signatures are rejected to keep the placeholder conservative.
        """
        if not signature:
            return False
        return bool(raw_payload)

    def hash_log_raw_event(self, raw_payload: dict[str, Any]) -> str:
        raw_repr = repr(sorted(raw_payload.items()))
        payload_hash = sha256(raw_repr.encode("utf-8")).hexdigest()
        self.store.events.append(
            PlatformEvent(
                event_id=str(uuid4()),
                platform=self.platform,
                event_type=PlatformEventType.PLATFORM_WARNING_RECEIVED,
                live_session_id=str(raw_payload.get("live_session_id", "unknown")),
                content="taobao_raw_event_hash_logged",
                raw_payload_hash=payload_hash,
                payload={"audit_only": True},
            ),
        )
        return payload_hash

    def bind_product(self, platform_product_id: str, product_id: str) -> PlatformProductMapping:
        mapping = PlatformProductMapping(
            platform=self.platform,
            platform_product_id=platform_product_id,
            product_id=product_id,
        )
        self.product_mappings[platform_product_id] = mapping
        return mapping

    def resolve_product_id(self, platform_product_id: str) -> str | None:
        mapping = self.product_mappings.get(platform_product_id)
        return mapping.product_id if mapping else None

    def normalize_comment_event(self, raw_payload: dict[str, Any]) -> PlatformEvent:
        live_session_id = self._require(raw_payload, "live_session_id")
        content = self._require(raw_payload, "content")
        return PlatformEvent(
            event_id=str(raw_payload.get("event_id") or uuid4()),
            platform=self.platform,
            event_type=PlatformEventType.COMMENT_RECEIVED,
            live_session_id=live_session_id,
            user_id_hash=self._hash_optional(raw_payload.get("user_id")),
            user_nickname=raw_payload.get("nickname"),
            content=content,
            raw_payload_hash=self._hash_raw_payload(raw_payload),
            payload={"platform_product_id": raw_payload.get("platform_product_id")},
        )

    def normalize_live_event(self, raw_payload: dict[str, Any]) -> PlatformEvent:
        live_session_id = self._require(raw_payload, "live_session_id")
        status = raw_payload.get("status")
        event_type = (
            PlatformEventType.LIVE_STARTED if status == "started" else PlatformEventType.LIVE_ENDED
        )
        return PlatformEvent(
            event_id=str(raw_payload.get("event_id") or uuid4()),
            platform=self.platform,
            event_type=event_type,
            live_session_id=live_session_id,
            raw_payload_hash=self._hash_raw_payload(raw_payload),
            payload={"status": status},
        )

    def normalize_order_event(self, raw_payload: dict[str, Any]) -> PlatformEvent:
        live_session_id = self._require(raw_payload, "live_session_id")
        order_id = self._require(raw_payload, "order_id")
        return PlatformEvent(
            event_id=str(raw_payload.get("event_id") or uuid4()),
            platform=self.platform,
            event_type=PlatformEventType.ORDER_CREATED,
            live_session_id=live_session_id,
            raw_payload_hash=self._hash_raw_payload(raw_payload),
            payload={
                "order_id_hash": self._hash_optional(order_id),
                "platform_product_id": raw_payload.get("platform_product_id"),
            },
        )

    @staticmethod
    def _require(raw_payload: dict[str, Any], key: str) -> str:
        value = raw_payload.get(key)
        if value in {None, ""}:
            raise DomainError(f"missing taobao raw event field: {key}")
        return str(value)

    @staticmethod
    def _hash_optional(value: object | None) -> str | None:
        if value is None:
            return None
        return sha256(str(value).encode("utf-8")).hexdigest()

    @classmethod
    def _hash_raw_payload(cls, raw_payload: dict[str, Any]) -> str:
        raw_repr = repr(sorted(raw_payload.items()))
        return sha256(raw_repr.encode("utf-8")).hexdigest()
