import pytest

pytest.importorskip("pydantic")

from app.core.errors import DomainError
from app.services import (
    AnswerCandidate,
    CandidateStatus,
    ComplianceService,
    HumanReviewService,
    InMemoryStore,
    MockTTSProvider,
    ProductService,
    ReviewStatus,
    Risk,
    TTSService,
)


def test_compliance_uses_split_checkers_for_low_medium_high_and_blocked() -> None:
    store = InMemoryStore()
    product = ProductService(store).create_product("修护霜")
    ProductService(store).add_sku(product.id, "默认", 19900, 10)
    service = ComplianceService()

    low = service.review_text("今天以页面价格为准", product)
    medium = service.review_text("敏感肌建议先咨询客服", product)
    high = service.review_text("保证不过敏", product)
    blocked = service.review_text("请私下转账", product)

    assert low.risk == Risk.LOW
    assert medium.risk == Risk.MEDIUM and medium.need_human_review
    assert high.risk == Risk.HIGH and high.need_human_review
    assert blocked.risk == Risk.BLOCKED and blocked.blocked


def test_product_forbidden_claim_checker_blocks_product_specific_claim() -> None:
    store = InMemoryStore()
    products = ProductService(store)
    product = products.create_product("修护霜")
    products.add_forbidden_claim(product.id, "三天祛斑")

    candidate = AnswerCandidate("comment-task-id", "坚持使用可以三天祛斑")
    ComplianceService().check(candidate, product=product)

    assert candidate.risk == Risk.BLOCKED
    assert candidate.status == CandidateStatus.BLOCKED
    assert "商品禁用表达" in candidate.matched_rules[0]


def test_human_review_supports_approve_reject_rewrite_and_manual_answer() -> None:
    store = InMemoryStore()
    candidate = AnswerCandidate("comment-task-id", "原始回答")
    store.candidates[candidate.id] = candidate
    service = HumanReviewService(store)

    approved = service.create(candidate)
    service.approve(approved.id, reviewer_id="reviewer-1")
    assert approved.status == ReviewStatus.APPROVED
    assert candidate.status == CandidateStatus.APPROVED

    rejected_candidate = AnswerCandidate("comment-task-id-2", "不合适回答")
    store.candidates[rejected_candidate.id] = rejected_candidate
    rejected = service.create(rejected_candidate)
    service.reject(rejected.id, reviewer_id="reviewer-2", reason="risk")
    assert rejected.status == ReviewStatus.REJECTED
    assert rejected_candidate.status == CandidateStatus.REJECTED

    rewritten_candidate = AnswerCandidate("comment-task-id-3", "待改写")
    store.candidates[rewritten_candidate.id] = rewritten_candidate
    rewritten = service.create(rewritten_candidate)
    service.rewrite(rewritten.id, reviewer_id="reviewer-3", rewritten_text="改写后通过")
    assert rewritten.final_text == "改写后通过"
    assert rewritten_candidate.text == "改写后通过"

    manual_candidate = AnswerCandidate("comment-task-id-4", "占位")
    store.candidates[manual_candidate.id] = manual_candidate
    manual = service.manual_answer(manual_candidate, reviewer_id="reviewer-4", manual_text="人工回答")
    assert manual.status == ReviewStatus.APPROVED
    assert manual.final_text == "人工回答"
    assert [log["action"] for log in store.audit_logs].count("rewrite") == 2


def test_human_review_rejects_reprocessing_completed_task() -> None:
    store = InMemoryStore()
    candidate = AnswerCandidate("comment-task-id", "回答")
    store.candidates[candidate.id] = candidate
    service = HumanReviewService(store)
    review = service.create(candidate)
    service.approve(review.id, reviewer_id="reviewer")

    with pytest.raises(DomainError):
        service.reject(review.id, reviewer_id="reviewer", reason="late")


def test_tts_service_caches_assets_precaches_and_surfaces_provider_failures() -> None:
    store = InMemoryStore()
    service = TTSService(store)

    first = service.generate("欢迎来到直播间")
    second = service.generate("欢迎来到直播间")
    precached = service.precache(["第一句", "第二句"])

    assert first is second
    assert first.audio_url.startswith("mock://audio/")
    assert len(precached) == 2
    assert len(store.tts_assets) == 3

    failing = TTSService(InMemoryStore(), provider=MockTTSProvider(fail=True))
    with pytest.raises(DomainError):
        failing.generate("会失败")
