from app.core.errors import DomainError
from app.services.entities import AnswerCandidate, CandidateStatus, HumanReviewTask, ReviewStatus
from app.services.store import InMemoryStore


class HumanReviewService:
    def __init__(self, store: InMemoryStore) -> None:
        self.store = store

    def create(self, candidate: AnswerCandidate) -> HumanReviewTask:
        task = HumanReviewTask(candidate_id=candidate.id)
        self.store.reviews[task.id] = task
        self._audit(task.id, "create", candidate_id=candidate.id)
        return task

    def approve(self, review_id: str, reviewer_id: str, text: str | None = None) -> HumanReviewTask:
        review = self._get_pending(review_id)
        candidate = self.store.candidates[review.candidate_id]
        review.status = ReviewStatus.APPROVED
        review.final_text = text or candidate.text
        review.reviewer_id = reviewer_id
        candidate.status = CandidateStatus.APPROVED
        self._audit(review_id, "approve", reviewer_id=reviewer_id)
        return review

    def reject(self, review_id: str, reviewer_id: str, reason: str) -> HumanReviewTask:
        review = self._get_pending(review_id)
        candidate = self.store.candidates[review.candidate_id]
        review.status = ReviewStatus.REJECTED
        review.reviewer_id = reviewer_id
        review.reason = reason
        candidate.status = CandidateStatus.REJECTED
        self._audit(review_id, "reject", reviewer_id=reviewer_id, reason=reason)
        return review

    def rewrite(self, review_id: str, reviewer_id: str, rewritten_text: str) -> HumanReviewTask:
        if not rewritten_text.strip():
            raise DomainError("rewritten text must not be empty")
        review = self._get_pending(review_id)
        candidate = self.store.candidates[review.candidate_id]
        review.status = ReviewStatus.APPROVED
        review.final_text = rewritten_text
        review.reviewer_id = reviewer_id
        candidate.text = rewritten_text
        candidate.status = CandidateStatus.APPROVED
        self._audit(review_id, "rewrite", reviewer_id=reviewer_id)
        return review

    def manual_answer(
        self,
        candidate: AnswerCandidate,
        reviewer_id: str,
        manual_text: str,
    ) -> HumanReviewTask:
        if not manual_text.strip():
            raise DomainError("manual answer must not be empty")
        task = self.create(candidate)
        return self.rewrite(task.id, reviewer_id=reviewer_id, rewritten_text=manual_text)

    def _get_pending(self, review_id: str) -> HumanReviewTask:
        review = self.store.reviews[review_id]
        if review.status != ReviewStatus.PENDING:
            raise DomainError(f"review task {review_id} is already {review.status}")
        return review

    def _audit(self, review_id: str, action: str, **metadata: object) -> None:
        self.store.audit_logs.append({"review_id": review_id, "action": action, **metadata})
