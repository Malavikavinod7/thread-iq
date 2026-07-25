from app.core.enums import ProductStatus
from app.models.product import Product
from app.repositories.product_repository import ProductRepository


class ProductService:
    """Application service containing product business rules."""

    def __init__(self, repository: ProductRepository) -> None:
        self._repository = repository

    def list_products(self) -> list[Product]:
        """Return only active products to the application layer."""
        products = self._repository.list_all()
        return [product for product in products if product.status == ProductStatus.ACTIVE]
