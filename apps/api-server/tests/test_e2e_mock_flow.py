import pytest

pytest.importorskip("pydantic")

from app.services import (
    AvatarGateway,
    CommentRouter,
    ComplianceService,
    HumanReviewService,
    InMemoryStore,
    LLMGateway,
    LiveSessionStateMachine,
    LiveState,
    MockPlatformAdapter,
    ProductRAG,
    ProductService,
    Risk,
    SpeechQueueService,
    TTSService,
)


def test_mock_comment_to_avatar_speech_flow() -> None:
    store = InMemoryStore()
    products = ProductService(store)
    product = products.create_product("保湿面霜")
    products.add_sku(product.id, "50ml", 12900, 88)
    products.add_faq(product.id, "这款多少钱", "今天以页面价格为准")
    products.add_selling_point(product.id, "温和保湿")

    rag = ProductRAG(store)
    rag.index_product(product)

    state_machine = LiveSessionStateMachine(store)
    session = state_machine.create(product.id)
    state_machine.transition(session.id, LiveState.LIVE, "start mock live")

    event = MockPlatformAdapter(store).comment(session.id, "这款多少钱？")
    task = CommentRouter(store).route(event)
    assert task is not None

    candidate = LLMGateway(store, rag).generate_product_answer(task)
    checked = ComplianceService().check(candidate, product=product)
    assert checked.risk == Risk.LOW

    state_machine.transition(session.id, LiveState.WAITING_REVIEW, "candidate needs review")
    review_service = HumanReviewService(store)
    review = review_service.create(checked)
    review_service.approve(review.id, reviewer_id="operator-1")

    state_machine.transition(session.id, LiveState.SPEAKING, "approved speech")
    speech_queue = SpeechQueueService(
        store,
        TTSService(store),
        AvatarGateway(store),
    )
    speech_queue.enqueue_reviewed_candidate(checked, review)
    speech = speech_queue.play_next()
    assert speech is not None
    state_machine.transition(session.id, LiveState.LIVE, "speech finished")
    task.status = "spoken"

    assert task.status == "spoken"
    assert checked.status.value == "approved"
    assert speech.status == "finished"
    assert len(store.state_logs) >= 4
    assert store.avatar_logs[-1]["status"] == "success"
    assert store.events[0].raw_payload_hash


def test_blocked_answer_never_creates_speech_task() -> None:
    store = InMemoryStore()
    products = ProductService(store)
    product = products.create_product("修护霜")
    products.add_sku(product.id, "默认", 9900, 10)
    candidate = LLMGateway(store, ProductRAG(store)).generate_product_answer(
        CommentRouter(store).route(
            MockPlatformAdapter(store).comment(
                LiveSessionStateMachine(store).create(product.id).id,
                "这款能治好湿疹吗？",
            ),
        ),
    )
    candidate.text = "这款能治好湿疹"
    checked = ComplianceService().check(candidate, product=product)
    review = HumanReviewService(store).create(checked)

    with pytest.raises(Exception):
        SpeechQueueService(store, TTSService(store), AvatarGateway(store)).enqueue_reviewed_candidate(
            checked,
            review,
        )

    assert checked.risk == Risk.BLOCKED
    assert store.speeches == {}
