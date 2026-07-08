from collections.abc import Sequence
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    AnswerCandidateModel,
    AuditLogModel,
    CommentTaskModel,
    HumanReviewTaskModel,
    LiveSessionModel,
    ProductFaqModel,
    ProductModel,
    ProductSellingPointModel,
    SkuModel,
    SpeechTaskModel,
)


class ProductRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_product(self, title: str) -> ProductModel:
        product = ProductModel(id=str(uuid4()), title=title)
        self.session.add(product)
        await self.session.flush()
        return product

    async def add_sku(
        self,
        product_id: str,
        name: str,
        price_cents: int,
        stock: int,
    ) -> SkuModel:
        sku = SkuModel(
            id=str(uuid4()),
            product_id=product_id,
            name=name,
            price_cents=price_cents,
            stock=stock,
        )
        self.session.add(sku)
        await self.session.flush()
        return sku

    async def add_faq(self, product_id: str, question: str, answer: str) -> ProductFaqModel:
        faq = ProductFaqModel(id=str(uuid4()), product_id=product_id, question=question, answer=answer)
        self.session.add(faq)
        await self.session.flush()
        return faq

    async def add_selling_point(self, product_id: str, text: str) -> ProductSellingPointModel:
        selling_point = ProductSellingPointModel(id=str(uuid4()), product_id=product_id, text=text)
        self.session.add(selling_point)
        await self.session.flush()
        return selling_point

    async def get(self, product_id: str) -> ProductModel | None:
        return await self.session.get(ProductModel, product_id)

    async def list(self) -> Sequence[ProductModel]:
        result = await self.session.execute(select(ProductModel))
        return result.scalars().all()


class LiveSessionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, product_id: str, state: str) -> LiveSessionModel:
        live_session = LiveSessionModel(id=str(uuid4()), product_id=product_id, state=state)
        self.session.add(live_session)
        await self.session.flush()
        return live_session

    async def set_state(self, live_session_id: str, state: str) -> LiveSessionModel:
        live_session = await self.session.get(LiveSessionModel, live_session_id)
        if live_session is None:
            raise KeyError(live_session_id)
        live_session.state = state
        await self.session.flush()
        return live_session


class CommentTaskRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        event_id: str,
        product_id: str,
        content: str,
        intent: str,
        status: str,
    ) -> CommentTaskModel:
        task = CommentTaskModel(
            id=str(uuid4()),
            event_id=event_id,
            product_id=product_id,
            content=content,
            intent=intent,
            status=status,
        )
        self.session.add(task)
        await self.session.flush()
        return task


class AnswerCandidateRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        comment_task_id: str,
        text: str,
        risk: str | None,
        status: str,
        need_human_review: bool,
    ) -> AnswerCandidateModel:
        candidate = AnswerCandidateModel(
            id=str(uuid4()),
            comment_task_id=comment_task_id,
            text=text,
            risk=risk,
            status=status,
            need_human_review=str(need_human_review).lower(),
        )
        self.session.add(candidate)
        await self.session.flush()
        return candidate


class HumanReviewTaskRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, candidate_id: str, status: str) -> HumanReviewTaskModel:
        task = HumanReviewTaskModel(id=str(uuid4()), candidate_id=candidate_id, status=status)
        self.session.add(task)
        await self.session.flush()
        return task

    async def set_approved(
        self,
        review_id: str,
        reviewer_id: str,
        final_text: str,
    ) -> HumanReviewTaskModel:
        task = await self.session.get(HumanReviewTaskModel, review_id)
        if task is None:
            raise KeyError(review_id)
        task.status = "approved"
        task.reviewer_id = reviewer_id
        task.final_text = final_text
        await self.session.flush()
        return task


class SpeechTaskRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        text: str,
        status: str,
        priority: int = 100,
        candidate_id: str | None = None,
        review_id: str | None = None,
    ) -> SpeechTaskModel:
        task = SpeechTaskModel(
            id=str(uuid4()),
            candidate_id=candidate_id,
            review_id=review_id,
            text=text,
            priority=priority,
            status=status,
        )
        self.session.add(task)
        await self.session.flush()
        return task

    async def set_status(
        self,
        speech_id: str,
        status: str,
        audio_url: str | None = None,
        failure_reason: str | None = None,
    ) -> SpeechTaskModel:
        task = await self.session.get(SpeechTaskModel, speech_id)
        if task is None:
            raise KeyError(speech_id)
        task.status = status
        task.audio_url = audio_url
        task.failure_reason = failure_reason
        await self.session.flush()
        return task


class AuditLogRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def append(
        self,
        entity_type: str,
        entity_id: str,
        action: str,
        actor_id: str | None = None,
        metadata_json: str = "{}",
    ) -> AuditLogModel:
        audit_log = AuditLogModel(
            id=str(uuid4()),
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            actor_id=actor_id,
            metadata_json=metadata_json,
        )
        self.session.add(audit_log)
        await self.session.flush()
        return audit_log
