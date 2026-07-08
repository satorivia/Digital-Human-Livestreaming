from fastapi import APIRouter, Depends

from app.api.dependencies import ServiceContainer, get_container
from app.api.schemas import (
    ApiResponse,
    FaqCreateRequest,
    LiveSessionCreateRequest,
    MockCommentRequest,
    ProductCreateRequest,
    ReviewApproveRequest,
    ReviewRejectRequest,
    ReviewRewriteRequest,
    SellingPointCreateRequest,
    SkuCreateRequest,
)
from app.core.errors import DomainError
from app.services import CandidateStatus, LiveState, Risk

router = APIRouter(prefix="/api/v1")


def ok(data: object) -> ApiResponse:
    return ApiResponse(data=data)


@router.post("/products", response_model=ApiResponse)
def create_product(
    request: ProductCreateRequest,
    services: ServiceContainer = Depends(get_container),
) -> ApiResponse:
    product = services.products.create_product(request.title)
    return ok(product)


@router.get("/products", response_model=ApiResponse)
def list_products(services: ServiceContainer = Depends(get_container)) -> ApiResponse:
    return ok(list(services.store.products.values()))


@router.get("/products/{product_id}", response_model=ApiResponse)
def get_product(product_id: str, services: ServiceContainer = Depends(get_container)) -> ApiResponse:
    return ok(services.store.products[product_id])


@router.post("/products/{product_id}/skus", response_model=ApiResponse)
def add_sku(
    product_id: str,
    request: SkuCreateRequest,
    services: ServiceContainer = Depends(get_container),
) -> ApiResponse:
    sku = services.products.add_sku(product_id, request.name, request.price_cents, request.stock)
    return ok(sku)


@router.post("/products/{product_id}/faqs", response_model=ApiResponse)
def add_faq(
    product_id: str,
    request: FaqCreateRequest,
    services: ServiceContainer = Depends(get_container),
) -> ApiResponse:
    product = services.products.add_faq(product_id, request.question, request.answer)
    return ok(product)


@router.post("/products/{product_id}/selling-points", response_model=ApiResponse)
def add_selling_point(
    product_id: str,
    request: SellingPointCreateRequest,
    services: ServiceContainer = Depends(get_container),
) -> ApiResponse:
    product = services.products.add_selling_point(product_id, request.text)
    return ok(product)


@router.post("/products/{product_id}/index", response_model=ApiResponse)
def index_product(product_id: str, services: ServiceContainer = Depends(get_container)) -> ApiResponse:
    product = services.store.products[product_id]
    services.rag.index_product(product)
    return ok({"indexed": True, "chunks": len(services.store.knowledge)})


@router.post("/live-sessions", response_model=ApiResponse)
def create_live_session(
    request: LiveSessionCreateRequest,
    services: ServiceContainer = Depends(get_container),
) -> ApiResponse:
    session = services.live_sessions.create(request.product_id)
    return ok(session)


@router.get("/live-sessions/{session_id}", response_model=ApiResponse)
def get_live_session(session_id: str, services: ServiceContainer = Depends(get_container)) -> ApiResponse:
    return ok(services.store.sessions[session_id])


@router.post("/live-sessions/{session_id}/start", response_model=ApiResponse)
def start_live_session(
    session_id: str,
    services: ServiceContainer = Depends(get_container),
) -> ApiResponse:
    session = services.live_sessions.transition(session_id, LiveState.LIVE, "api_start")
    services.platform.live_started(session_id)
    return ok(session)


@router.post("/live-sessions/{session_id}/end", response_model=ApiResponse)
def end_live_session(session_id: str, services: ServiceContainer = Depends(get_container)) -> ApiResponse:
    session = services.live_sessions.transition(session_id, LiveState.ENDED, "api_end")
    return ok(session)


@router.get("/live-sessions/{session_id}/state-logs", response_model=ApiResponse)
def get_state_logs(session_id: str, services: ServiceContainer = Depends(get_container)) -> ApiResponse:
    logs = [log for log in services.store.state_logs if log["session_id"] == session_id]
    return ok(logs)


@router.post("/live-sessions/{session_id}/mock-comments", response_model=ApiResponse)
def create_mock_comment(
    session_id: str,
    request: MockCommentRequest,
    services: ServiceContainer = Depends(get_container),
) -> ApiResponse:
    event = services.platform.comment(session_id, request.content, user=request.user)
    comment_task = services.comments.route(event)
    if comment_task is None:
        raise DomainError("comment was ignored by router")
    candidate = services.llm.generate_product_answer(comment_task)
    product = services.store.products[comment_task.product_id]
    checked = services.compliance.check(candidate, product=product)
    review = services.reviews.create(checked)
    return ok({"event": event, "comment_task": comment_task, "candidate": checked, "review": review})


@router.get("/live-sessions/{session_id}/comments", response_model=ApiResponse)
def list_comments(session_id: str, services: ServiceContainer = Depends(get_container)) -> ApiResponse:
    session = services.store.sessions[session_id]
    comments = [task for task in services.store.comments.values() if task.product_id == session.product_id]
    return ok(comments)


@router.post("/comment-tasks/{task_id}/answer-candidates", response_model=ApiResponse)
def generate_answer_candidate(
    task_id: str,
    services: ServiceContainer = Depends(get_container),
) -> ApiResponse:
    task = services.store.comments[task_id]
    candidate = services.llm.generate_product_answer(task)
    product = services.store.products[task.product_id]
    checked = services.compliance.check(candidate, product=product)
    review = services.reviews.create(checked)
    return ok({"candidate": checked, "review": review})


@router.get("/review-tasks", response_model=ApiResponse)
def list_review_tasks(services: ServiceContainer = Depends(get_container)) -> ApiResponse:
    return ok(list(services.store.reviews.values()))


@router.post("/review-tasks/{review_id}/approve", response_model=ApiResponse)
def approve_review(
    review_id: str,
    request: ReviewApproveRequest,
    services: ServiceContainer = Depends(get_container),
) -> ApiResponse:
    pending_review = services.store.reviews[review_id]
    candidate = services.store.candidates[pending_review.candidate_id]
    if candidate.risk == Risk.BLOCKED or candidate.status == CandidateStatus.BLOCKED:
        raise DomainError("blocked answers must never be played")
    review = services.reviews.approve(review_id, reviewer_id=request.reviewer_id, text=request.text)
    speech = services.speech.enqueue_reviewed_candidate(candidate, review)
    return ok({"review": review, "speech_task": speech})


@router.post("/review-tasks/{review_id}/reject", response_model=ApiResponse)
def reject_review(
    review_id: str,
    request: ReviewRejectRequest,
    services: ServiceContainer = Depends(get_container),
) -> ApiResponse:
    review = services.reviews.reject(review_id, reviewer_id=request.reviewer_id, reason=request.reason)
    return ok(review)


@router.post("/review-tasks/{review_id}/rewrite", response_model=ApiResponse)
def rewrite_review(
    review_id: str,
    request: ReviewRewriteRequest,
    services: ServiceContainer = Depends(get_container),
) -> ApiResponse:
    review = services.reviews.rewrite(
        review_id,
        reviewer_id=request.reviewer_id,
        rewritten_text=request.text,
    )
    candidate = services.store.candidates[review.candidate_id]
    speech = services.speech.enqueue_reviewed_candidate(candidate, review)
    return ok({"review": review, "speech_task": speech})


@router.get("/speech-tasks", response_model=ApiResponse)
def list_speech_tasks(services: ServiceContainer = Depends(get_container)) -> ApiResponse:
    return ok(list(services.store.speeches.values()))


@router.post("/speech-tasks/{speech_id}/play", response_model=ApiResponse)
def play_speech_task(speech_id: str, services: ServiceContainer = Depends(get_container)) -> ApiResponse:
    task = services.store.speeches[speech_id]
    if services.speech.next_task() != task:
        raise DomainError("speech task is not next in queue")
    played = services.speech.play_next()
    return ok(played)


@router.post("/speech-tasks/{speech_id}/interrupt", response_model=ApiResponse)
def interrupt_speech_task(
    speech_id: str,
    services: ServiceContainer = Depends(get_container),
) -> ApiResponse:
    task = services.store.speeches[speech_id]
    interrupted = services.speech.mark_interrupted(task)
    return ok(interrupted)
