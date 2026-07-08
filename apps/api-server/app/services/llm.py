from app.services.entities import AnswerCandidate, CommentTask
from app.services.rag import ProductRAG
from app.services.store import InMemoryStore


class LLMGateway:
    def __init__(self, store: InMemoryStore, rag: ProductRAG) -> None:
        self.store = store
        self.rag = rag

    def generate_product_answer(self, task: CommentTask) -> AnswerCandidate:
        product = self.store.products[task.product_id]
        retrieved_chunks = self.rag.search(product.id, task.content)
        if task.intent == "price":
            price_text = "以商品页为准"
            if product.skus:
                price_text = f"参考SKU价格为{product.skus[0].price_cents / 100:.2f}元，最终以页面为准"
            text = f"这款{product.title}当前价格{price_text}。"
        else:
            facts = retrieved_chunks or product.selling_points[:2]
            text = f"这款{product.title}的已登记卖点是：{'；'.join(facts)}。"

        candidate = AnswerCandidate(comment_task_id=task.id, text=text)
        self.store.candidates[candidate.id] = candidate
        self.store.llm_logs.append({"candidate_id": candidate.id, "provider": "mock"})
        return candidate
