from dataclasses import dataclass

from app.services import (
    AvatarGateway,
    CommentRouter,
    ComplianceService,
    HumanReviewService,
    InMemoryStore,
    LLMGateway,
    LiveSessionStateMachine,
    MockPlatformAdapter,
    ProductRAG,
    ProductService,
    SpeechQueueService,
    TTSService,
)


@dataclass(slots=True)
class ServiceContainer:
    store: InMemoryStore
    products: ProductService
    rag: ProductRAG
    live_sessions: LiveSessionStateMachine
    platform: MockPlatformAdapter
    comments: CommentRouter
    llm: LLMGateway
    compliance: ComplianceService
    reviews: HumanReviewService
    tts: TTSService
    avatar: AvatarGateway
    speech: SpeechQueueService


def create_container() -> ServiceContainer:
    store = InMemoryStore()
    rag = ProductRAG(store)
    tts = TTSService(store)
    avatar = AvatarGateway(store)
    return ServiceContainer(
        store=store,
        products=ProductService(store),
        rag=rag,
        live_sessions=LiveSessionStateMachine(store),
        platform=MockPlatformAdapter(store),
        comments=CommentRouter(store),
        llm=LLMGateway(store, rag),
        compliance=ComplianceService(),
        reviews=HumanReviewService(store),
        tts=tts,
        avatar=avatar,
        speech=SpeechQueueService(store, tts, avatar),
    )


container = create_container()


def get_container() -> ServiceContainer:
    return container
