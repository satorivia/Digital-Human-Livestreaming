from app.services.domain import *

def test_state_machine():
    st=Store(); ps=ProductService(st); p=ps.create_product('面霜'); sm=LiveSessionStateMachine(st); s=sm.create(p.id)
    sm.transition(s.id,LiveState.LIVE,'start')
    try: sm.transition(s.id,LiveState.SPEAKING,'bad')
    except ValueError: pass
    else: raise AssertionError('illegal transition not rejected')
    assert st.state_logs[0]['to']==LiveState.LIVE

def test_product_rag_and_compliance():
    st=Store(); ps=ProductService(st); p=ps.create_product('面霜'); ps.add_sku(p.id,'默认',9900,10); ps.add_faq(p.id,'这款多少钱','页面价格为准'); rag=ProductRAG(st); rag.index_product(p)
    c=Candidate('t','保证不过敏，100%有效'); ComplianceService().check(c)
    assert c.risk==Risk.HIGH
    assert rag.search(p.id,'这款多少钱')

def test_comment_router_dedup():
    st=Store(); p=ProductService(st).create_product('面霜'); sm=LiveSessionStateMachine(st); s=sm.create(p.id); sm.transition(s.id,LiveState.LIVE,'start')
    e=MockPlatformAdapter(st).comment(s.id,'这款多少钱？')
    router=CommentRouter(st); assert router.route(e); assert router.route(e) is None
