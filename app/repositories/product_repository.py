import uuid
from abc import ABC, abstractmethod

from app.core.enums import ProductStatus
from app.models.product import Product


class ProductRepository(ABC):
    """Persistence boundary for product data access."""

    @abstractmethod
    def list_all(self) -> list[Product]:
        """Return all products from the storage layer."""
        raise NotImplementedError


class InMemoryProductRepository(ProductRepository):
    """In-memory repository used for demo and test environments."""

    def __init__(self) -> None:
        self._products: list[Product] = [
            Product(id=uuid.uuid4(), name="Sample product", status=ProductStatus.ACTIVE)
        ]

    def list_all(self) -> list[Product]:
        return list(self._products)
