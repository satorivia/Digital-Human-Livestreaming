from app.services.domain import *

def test_mock_comment_to_avatar_speech_flow():
    store=Store(); products=ProductService(store); product=products.create_product('保湿面霜')
    products.add_sku(product.id,'50ml',12900,88); products.add_faq(product.id,'这款多少钱','今天以页面价格为准'); products.add_selling_point(product.id,'温和保湿')
    rag=ProductRAG(store); rag.index_product(product)
    sm=LiveSessionStateMachine(store); session=sm.create(product.id); sm.transition(session.id,LiveState.LIVE,'start mock live')
    event=MockPlatformAdapter(store).comment(session.id,'这款多少钱？')
    task=CommentRouter(store).route(event); assert task is not None
    candidate=LLMGateway(store,rag).generate_product_answer(task)
    checked=ComplianceService().check(candidate); assert checked.risk==Risk.LOW
    sm.transition(session.id,LiveState.WAITING_REVIEW,'candidate needs review')
    review=HumanReviewService(store).create(checked); HumanReviewService(store).approve(review.id)
    sm.transition(session.id,LiveState.SPEAKING,'approved speech')
    speech=SpeechQueueService(store,TTSService(store),AvatarGateway(store)).enqueue_and_play(review.final_text or checked.text)
    sm.transition(session.id,LiveState.LIVE,'speech finished')
    task.status='spoken'
    assert task.status=='spoken'; assert checked.status=='approved'; assert speech.status=='finished'
    assert len(store.state_logs)>=4; assert store.avatar_logs[-1]['status']=='success'; assert store.events[0].raw_payload_hash
