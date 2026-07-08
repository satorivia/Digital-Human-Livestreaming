from app.core.errors import DomainError
from app.services.avatar import AvatarGateway
from app.services.entities import (
    AnswerCandidate,
    CandidateStatus,
    HumanReviewTask,
    ReviewStatus,
    Risk,
    SpeechStatus,
    SpeechTask,
)
from app.services.store import InMemoryStore
from app.services.tts import TTSService


class SpeechQueueService:
    def __init__(self, store: InMemoryStore, tts: TTSService, avatar: AvatarGateway) -> None:
        self.store = store
        self.tts = tts
        self.avatar = avatar

    def enqueue_speech(
        self,
        text: str,
        priority: int = 100,
        candidate_id: str | None = None,
        review_id: str | None = None,
    ) -> SpeechTask:
        task = SpeechTask(text=text, priority=priority, candidate_id=candidate_id, review_id=review_id)
        self.store.speeches[task.id] = task
        return task

    def enqueue_reviewed_candidate(
        self,
        candidate: AnswerCandidate,
        review: HumanReviewTask,
        priority: int = 100,
    ) -> SpeechTask:
        if candidate.risk == Risk.BLOCKED or candidate.status == CandidateStatus.BLOCKED:
            raise DomainError("blocked answers must never be played")
        if candidate.status != CandidateStatus.APPROVED or review.status != ReviewStatus.APPROVED:
            raise DomainError("speech requires approved candidate and human review")
        if not review.final_text:
            raise DomainError("approved review must include final text")
        return self.enqueue_speech(
            review.final_text,
            priority=priority,
            candidate_id=candidate.id,
            review_id=review.id,
        )

    def next_task(self) -> SpeechTask | None:
        queued = [task for task in self.store.speeches.values() if task.status == SpeechStatus.QUEUED]
        if not queued:
            return None
        return sorted(queued, key=lambda task: (task.priority, task.id))[0]

    def mark_speaking(self, task: SpeechTask) -> SpeechTask:
        task.status = SpeechStatus.SPEAKING
        return task

    def mark_finished(self, task: SpeechTask) -> SpeechTask:
        task.status = SpeechStatus.FINISHED
        return task

    def mark_interrupted(self, task: SpeechTask) -> SpeechTask:
        task.status = SpeechStatus.INTERRUPTED
        self.avatar.interrupt(task)
        return task

    def mark_failed(self, task: SpeechTask, reason: str) -> SpeechTask:
        task.status = SpeechStatus.FAILED
        task.failure_reason = reason
        return task

    def play_next(self) -> SpeechTask | None:
        task = self.next_task()
        if task is None:
            return None
        try:
            asset = self.tts.generate(task.text)
            task.audio_url = asset.audio_url
            self.mark_speaking(task)
            return self.avatar.speak_audio(task)
        except DomainError as exc:
            self.mark_failed(task, str(exc))
            raise

    def enqueue_and_play(self, text: str, priority: int = 100) -> SpeechTask:
        self.enqueue_speech(text, priority=priority)
        task = self.play_next()
        if task is None:
            raise RuntimeError("speech queue unexpectedly empty")
        return task
