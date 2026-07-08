from app.services.entities import Product
from app.services.store import InMemoryStore


class ProductRAG:
    def __init__(self, store: InMemoryStore) -> None:
        self.store = store

    def index_product(self, product: Product) -> None:
        faq_chunks = [f"{question} {answer}" for question, answer in product.faqs.items()]
        chunks = faq_chunks + product.selling_points
        self.store.knowledge.extend((product.id, chunk) for chunk in chunks)

    def search(self, product_id: str, query: str, limit: int = 3) -> list[str]:
        normalized_query = query.lower().replace("？", " ").replace("?", " ")
        query_terms = set(normalized_query.split())
        matches: list[str] = []
        for indexed_product_id, text in self.store.knowledge:
            if indexed_product_id != product_id:
                continue
            normalized_text = text.lower()
            if query_terms & set(normalized_text.split()) or "多少" in query or "价格" in text:
                matches.append(text)
        return matches[:limit]
