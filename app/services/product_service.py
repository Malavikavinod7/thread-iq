from app.core.enums import ProductStatus
from app.models.product import Product
from app.repositories.product_repository import ProductRepository


class ProductService:

    def __init__(self, repository: ProductRepository):
        self.repository = repository

    def create_product(self, product: Product):
        return self.repository.create(product)

    def list_products(self):
        return self.repository.list_all()

    def get_product(self, product_id):
        return self.repository.get_by_id(product_id)
