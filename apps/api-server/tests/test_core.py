import pytest

pytest.importorskip("pydantic")

from app.services import (
    AnswerCandidate,
    CommentRouter,
    ComplianceService,
    IllegalLiveStateTransition,
    InMemoryStore,
    LiveSessionStateMachine,
    LiveState,
    MockPlatformAdapter,
    ProductRAG,
    ProductService,
    Risk,
)


def test_state_machine_records_legal_transitions_and_rejects_illegal_transition() -> None:
    store = InMemoryStore()
    product = ProductService(store).create_product("面霜")
    state_machine = LiveSessionStateMachine(store)
    session = state_machine.create(product.id)

    state_machine.transition(session.id, LiveState.LIVE, "start")

    with pytest.raises(IllegalLiveStateTransition):
        state_machine.transition(session.id, LiveState.SPEAKING, "bad")

    assert store.state_logs[0]["to"] == LiveState.LIVE


def test_product_rag_indexes_faq_and_compliance_classifies_high_risk_claim() -> None:
    store = InMemoryStore()
    products = ProductService(store)
    product = products.create_product("面霜")
    products.add_sku(product.id, "默认", 9900, 10)
    products.add_faq(product.id, "这款多少钱", "今天以页面价格为准")

    rag = ProductRAG(store)
    rag.index_product(product)

    candidate = AnswerCandidate("comment-task-id", "保证不过敏，100%有效")
    ComplianceService().check(candidate, product=product)

    assert candidate.risk == Risk.HIGH
    assert rag.search(product.id, "这款多少钱")


def test_comment_router_deduplicates_events_and_binds_current_product() -> None:
    store = InMemoryStore()
    product = ProductService(store).create_product("面霜")
    state_machine = LiveSessionStateMachine(store)
    session = state_machine.create(product.id)
    state_machine.transition(session.id, LiveState.LIVE, "start")
    event = MockPlatformAdapter(store).comment(session.id, "这款多少钱？")

    router = CommentRouter(store)
    task = router.route(event)

    assert task is not None
    assert task.product_id == product.id
    assert router.route(event) is None
