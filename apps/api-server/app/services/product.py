from app.services.entities import Product, SKU
from app.services.store import InMemoryStore


class ProductService:
    def __init__(self, store: InMemoryStore) -> None:
        self.store = store

    def create_product(self, title: str) -> Product:
        product = Product(title=title)
        self.store.products[product.id] = product
        return product

    def add_sku(self, product_id: str, name: str, price_cents: int, stock: int) -> SKU:
        sku = SKU(name=name, price_cents=price_cents, stock=stock)
        self.store.products[product_id].skus.append(sku)
        return sku

    def add_faq(self, product_id: str, question: str, answer: str) -> Product:
        product = self.store.products[product_id]
        product.faqs[question] = answer
        return product

    def add_selling_point(self, product_id: str, text: str) -> Product:
        product = self.store.products[product_id]
        product.selling_points.append(text)
        return product

    def add_forbidden_claim(self, product_id: str, text: str) -> Product:
        product = self.store.products[product_id]
        product.forbidden.append(text)
        return product
