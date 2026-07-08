import pytest

pytest.importorskip("pydantic")

from event_schema import PlatformEventType

from app.core.errors import DomainError
from app.services import InMemoryStore, TaobaoLiveAdapter, TaobaoLiveAdapterConfig


def make_adapter() -> TaobaoLiveAdapter:
    config = TaobaoLiveAdapterConfig(app_key="mock-app", enabled=False, sandbox=True)
    return TaobaoLiveAdapter(InMemoryStore(), config)


def test_taobao_config_masks_secret_values() -> None:
    config = TaobaoLiveAdapterConfig(app_key="mock-app", app_secret="secret-value")

    assert "secret-value" not in repr(config)


def test_taobao_adapter_rejects_missing_signature_placeholder() -> None:
    adapter = make_adapter()

    assert adapter.verify_signature_placeholder("{}", signature=None) is False
    assert adapter.verify_signature_placeholder("{}", signature="mock-signature") is True


def test_taobao_adapter_normalizes_comment_live_and_order_events() -> None:
    adapter = make_adapter()
    comment = adapter.normalize_comment_event(
        {
            "event_id": "comment-1",
            "live_session_id": "live-1",
            "content": "这款多少钱？",
            "user_id": "user-1",
            "nickname": "用户A",
            "platform_product_id": "tb-product-1",
        },
    )
    live_started = adapter.normalize_live_event(
        {"event_id": "live-start", "live_session_id": "live-1", "status": "started"},
    )
    order = adapter.normalize_order_event(
        {
            "event_id": "order-1",
            "live_session_id": "live-1",
            "order_id": "real-order-id",
            "platform_product_id": "tb-product-1",
        },
    )

    assert comment.event_type == PlatformEventType.COMMENT_RECEIVED
    assert comment.user_id_hash is not None
    assert comment.raw_payload_hash is not None
    assert live_started.event_type == PlatformEventType.LIVE_STARTED
    assert order.event_type == PlatformEventType.ORDER_CREATED
    assert order.payload["order_id_hash"] != "real-order-id"


def test_taobao_adapter_hash_logs_raw_events_and_maps_products() -> None:
    adapter = make_adapter()
    payload_hash = adapter.hash_log_raw_event({"live_session_id": "live-1", "raw": "payload"})
    mapping = adapter.bind_product("tb-product-1", "product-1")

    assert payload_hash == adapter.store.events[-1].raw_payload_hash
    assert mapping.product_id == "product-1"
    assert adapter.resolve_product_id("tb-product-1") == "product-1"


def test_taobao_adapter_requires_mandatory_fields() -> None:
    adapter = make_adapter()

    with pytest.raises(DomainError):
        adapter.normalize_comment_event({"live_session_id": "live-1"})
