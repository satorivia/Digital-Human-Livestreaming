import pytest

pytest.importorskip("pydantic")

from app.core.errors import DomainError
from app.services import (
    AnswerCandidate,
    AvatarGateway,
    CandidateStatus,
    HumanReviewService,
    InMemoryStore,
    ReviewStatus,
    Risk,
    SpeechQueueService,
    SpeechStatus,
    TTSService,
)


def test_avatar_gateway_supports_speak_text_interrupt_idle_and_failure_logs() -> None:
    store = InMemoryStore()
    avatar = AvatarGateway(store)
    queue = SpeechQueueService(store, TTSService(store), avatar)
    speech = queue.enqueue_speech("正在播报")
    queue.mark_speaking(speech)

    avatar.speak_text("欢迎")
    interrupted = avatar.interrupt(speech)
    avatar.idle()

    assert interrupted is speech
    assert speech.status == SpeechStatus.INTERRUPTED
    assert [log["command"] for log in store.avatar_logs] == ["speak_text", "interrupt", "idle"]

    failing = AvatarGateway(store, fail=True)
    with pytest.raises(DomainError):
        failing.speak_audio(queue.enqueue_speech("失败播报"))
    assert store.avatar_logs[-1]["status"] == "failed"


def test_speech_queue_orders_by_priority_and_marks_statuses() -> None:
    store = InMemoryStore()
    queue = SpeechQueueService(store, TTSService(store), AvatarGateway(store))
    low_priority = queue.enqueue_speech("后播", priority=100)
    high_priority = queue.enqueue_speech("先播", priority=1)

    assert queue.next_task() == high_priority

    played = queue.play_next()
    assert played == high_priority
    assert played.status == SpeechStatus.FINISHED
    assert low_priority.status == SpeechStatus.QUEUED

    queue.mark_failed(low_priority, "manual failure")
    assert low_priority.status == SpeechStatus.FAILED
    assert low_priority.failure_reason == "manual failure"


def test_speech_queue_requires_approved_human_review_and_blocks_blocked_answers() -> None:
    store = InMemoryStore()
    queue = SpeechQueueService(store, TTSService(store), AvatarGateway(store))
    review_service = HumanReviewService(store)

    blocked_candidate = AnswerCandidate("comment-task", "请私下转账")
    blocked_candidate.risk = Risk.BLOCKED
    blocked_candidate.status = CandidateStatus.BLOCKED
    blocked_review = review_service.create(blocked_candidate)

    with pytest.raises(DomainError):
        queue.enqueue_reviewed_candidate(blocked_candidate, blocked_review)

    approved_candidate = AnswerCandidate("comment-task-2", "今天以页面价格为准")
    store.candidates[approved_candidate.id] = approved_candidate
    approved_review = review_service.create(approved_candidate)
    review_service.approve(approved_review.id, reviewer_id="operator")

    speech = queue.enqueue_reviewed_candidate(approved_candidate, approved_review)
    assert speech.candidate_id == approved_candidate.id
    assert speech.review_id == approved_review.id
    assert speech.status == SpeechStatus.QUEUED

    pending_candidate = AnswerCandidate("comment-task-3", "待审核")
    pending_review = review_service.create(pending_candidate)
    assert pending_review.status == ReviewStatus.PENDING
    with pytest.raises(DomainError):
        queue.enqueue_reviewed_candidate(pending_candidate, pending_review)


def test_speech_queue_marks_tts_and_avatar_failures() -> None:
    from app.services import MockTTSProvider

    store = InMemoryStore()
    tts_failing_queue = SpeechQueueService(
        store,
        TTSService(store, provider=MockTTSProvider(fail=True)),
        AvatarGateway(store),
    )
    tts_task = tts_failing_queue.enqueue_speech("tts failure")
    with pytest.raises(DomainError):
        tts_failing_queue.play_next()
    assert tts_task.status == SpeechStatus.FAILED
    assert "tts" in (tts_task.failure_reason or "")

    avatar_store = InMemoryStore()
    avatar_failing_queue = SpeechQueueService(
        avatar_store,
        TTSService(avatar_store),
        AvatarGateway(avatar_store, fail=True),
    )
    avatar_task = avatar_failing_queue.enqueue_speech("avatar failure")
    with pytest.raises(DomainError):
        avatar_failing_queue.play_next()
    assert avatar_task.status == SpeechStatus.FAILED
    assert avatar_store.avatar_logs[-1]["status"] == "failed"
