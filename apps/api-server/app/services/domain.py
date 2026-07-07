from dataclasses import dataclass, field
from enum import StrEnum
from hashlib import sha256
from uuid import uuid4
from event_schema import PlatformEvent, PlatformEventType

class LiveState(StrEnum): CREATED='created'; LIVE='live'; WAITING_REVIEW='waiting_review'; SPEAKING='speaking'; HUMAN_TAKEOVER='human_takeover'; ENDED='ended'
class Risk(StrEnum): LOW='low'; MEDIUM='medium'; HIGH='high'; BLOCKED='blocked'

@dataclass
class SKU: name:str; price_cents:int; stock:int; id:str=field(default_factory=lambda:str(uuid4()))
@dataclass
class Product: title:str; id:str=field(default_factory=lambda:str(uuid4())); skus:list[SKU]=field(default_factory=list); faqs:dict[str,str]=field(default_factory=dict); selling_points:list[str]=field(default_factory=list); forbidden:list[str]=field(default_factory=list)
@dataclass
class LiveSession: product_id:str; id:str=field(default_factory=lambda:str(uuid4())); state:LiveState=LiveState.CREATED
@dataclass
class CommentTask: event_id:str; content:str; product_id:str; intent:str; status:str='pending'; id:str=field(default_factory=lambda:str(uuid4()))
@dataclass
class Candidate: comment_task_id:str; text:str; risk:Risk|None=None; status:str='generated'; id:str=field(default_factory=lambda:str(uuid4()))
@dataclass
class ReviewTask: candidate_id:str; status:str='pending'; final_text:str|None=None; id:str=field(default_factory=lambda:str(uuid4()))
@dataclass
class SpeechTask: text:str; audio_url:str|None=None; status:str='queued'; id:str=field(default_factory=lambda:str(uuid4()))

class Store:
    def __init__(self):
        self.products={}; self.sessions={}; self.events=[]; self.state_logs=[]; self.comments={}; self.candidates={}; self.reviews={}; self.speeches={}; self.audit_logs=[]; self.avatar_logs=[]; self.llm_logs=[]; self.tts_assets=[]; self.knowledge=[]

class ProductService:
    def __init__(self, store:Store): self.store=store
    def create_product(self,title:str)->Product:
        p=Product(title); self.store.products[p.id]=p; return p
    def add_sku(self,pid:str,name:str,price_cents:int,stock:int)->SKU:
        sku=SKU(name,price_cents,stock); self.store.products[pid].skus.append(sku); return sku
    def add_faq(self,pid:str,q:str,a:str): self.store.products[pid].faqs[q]=a; return self.store.products[pid]
    def add_selling_point(self,pid:str,text:str): self.store.products[pid].selling_points.append(text); return self.store.products[pid]

class ProductRAG:
    def __init__(self, store:Store): self.store=store
    def index_product(self,p:Product):
        self.store.knowledge += [(p.id,q+' '+a) for q,a in p.faqs.items()] + [(p.id,x) for x in p.selling_points]
    def search(self,pid:str,query:str)->list[str]:
        terms=set(query.lower().replace('？','').split())
        return [txt for p,txt in self.store.knowledge if p==pid and (terms & set(txt.lower().split()) or '多少' in query or '价格' in txt)][:3]

class MockPlatformAdapter:
    def __init__(self, store:Store): self.store=store
    def comment(self,session_id:str,content:str,user='观众')->PlatformEvent:
        e=PlatformEvent(event_id=str(uuid4()), event_type=PlatformEventType.COMMENT_RECEIVED, live_session_id=session_id, user_id_hash=sha256(user.encode()).hexdigest(), user_nickname=user, content=content, raw_payload_hash=sha256(content.encode()).hexdigest())
        self.store.events.append(e); return e

class LiveSessionStateMachine:
    allowed={(LiveState.CREATED,LiveState.LIVE),(LiveState.LIVE,LiveState.WAITING_REVIEW),(LiveState.WAITING_REVIEW,LiveState.SPEAKING),(LiveState.SPEAKING,LiveState.LIVE),(LiveState.LIVE,LiveState.HUMAN_TAKEOVER),(LiveState.HUMAN_TAKEOVER,LiveState.LIVE),(LiveState.LIVE,LiveState.ENDED)}
    def __init__(self,store:Store): self.store=store
    def create(self,pid:str): s=LiveSession(pid); self.store.sessions[s.id]=s; return s
    def transition(self,sid:str,to:LiveState,reason:str):
        s=self.store.sessions[sid]
        if (s.state,to) not in self.allowed: raise ValueError(f'illegal transition {s.state}->{to}')
        old=s.state; s.state=to; self.store.state_logs.append({'session_id':sid,'from':old,'to':to,'reason':reason}); return s

class CommentRouter:
    def __init__(self,store:Store): self.store=store; self.seen: set[str]=set()
    def route(self,e:PlatformEvent)->CommentTask|None:
        if e.event_type not in {PlatformEventType.COMMENT_RECEIVED,PlatformEventType.MANUAL_COMMENT_ENTERED}: return None
        if e.event_id in self.seen or any(x in (e.content or '') for x in ['拉黑','spam']): return None
        self.seen.add(e.event_id); sess=self.store.sessions[e.live_session_id]
        intent='price' if any(x in (e.content or '') for x in ['多少钱','价格','几块']) else 'product_qa'
        t=CommentTask(e.event_id,e.content or '',sess.product_id,intent); self.store.comments[t.id]=t; return t

class LLMGateway:
    def __init__(self,store:Store,rag:ProductRAG): self.store=store; self.rag=rag
    def generate_product_answer(self,task:CommentTask)->Candidate:
        p=self.store.products[task.product_id]; ctx=self.rag.search(p.id,task.content)
        price = f"{p.skus[0].price_cents/100:.2f}元" if p.skus else '以商品页为准'
        text = f"这款{p.title}当前价格以页面为准，参考SKU价格为{price}。" if task.intent=='price' else f"这款{p.title}的卖点是：{'；'.join(ctx or p.selling_points[:2])}。"
        c=Candidate(task.id,text); self.store.candidates[c.id]=c; self.store.llm_logs.append({'candidate_id':c.id,'provider':'mock'}); return c

class ComplianceService:
    blocked=['私下转账','治好湿疹']; high=['100%','保证不过敏','绝对']; medium=['敏感肌']
    def check(self,c:Candidate)->Candidate:
        text=c.text
        c.risk = Risk.BLOCKED if any(x in text for x in self.blocked) else Risk.HIGH if any(x in text for x in self.high) else Risk.MEDIUM if any(x in text for x in self.medium) else Risk.LOW
        c.status='blocked' if c.risk==Risk.BLOCKED else 'needs_human_review'
        return c

class HumanReviewService:
    def __init__(self,store:Store): self.store=store
    def create(self,c:Candidate)->ReviewTask:
        r=ReviewTask(c.id); self.store.reviews[r.id]=r; return r
    def approve(self,rid:str,text:str|None=None)->ReviewTask:
        r=self.store.reviews[rid]; c=self.store.candidates[r.candidate_id]; r.status='approved'; r.final_text=text or c.text; c.status='approved'; self.store.audit_logs.append({'review_id':rid,'action':'approve'}); return r
    def reject(self,rid:str): r=self.store.reviews[rid]; r.status='rejected'; self.store.audit_logs.append({'review_id':rid,'action':'reject'}); return r

class TTSService:
    def __init__(self,store:Store): self.store=store
    def generate(self,text:str):
        url='mock://audio/'+sha256(text.encode()).hexdigest()+'.wav'; self.store.tts_assets.append({'url':url,'provider':'mock'}); return url

class AvatarGateway:
    def __init__(self,store:Store): self.store=store
    def speak_audio(self,speech:SpeechTask): speech.status='finished'; self.store.avatar_logs.append({'speech_id':speech.id,'status':'success'}); return speech
    def interrupt(self): self.store.avatar_logs.append({'command':'interrupt','status':'success'})

class SpeechQueueService:
    def __init__(self,store:Store,tts:TTSService,avatar:AvatarGateway): self.store=store; self.tts=tts; self.avatar=avatar
    def enqueue_and_play(self,text:str)->SpeechTask:
        s=SpeechTask(text); self.store.speeches[s.id]=s; s.audio_url=self.tts.generate(text); s.status='speaking'; return self.avatar.speak_audio(s)

class MediaService:
    def preview_url(self,stream_key:str)->dict[str,str]: return {'webrtc_url':f'http://localhost:8080/live/{stream_key}.flv','status':'mock_ready'}
