import uuid
from abc import ABC, abstractmethod
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.enums import ProductStatus
from app.models.product import Product


class ProductRepository(ABC):

    @abstractmethod
    def create(self, product: Product) -> Product:
        ...

    @abstractmethod
    def list_all(self) -> list[Product]:
        ...

    @abstractmethod
    def get_by_id(self, product_id: UUID) -> Product | None:
        ...


class SQLAlchemyProductRepository(ProductRepository):

    def __init__(self, db: Session):
        self.db = db

    def create(self, product: Product) -> Product:
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product

    def list_all(self) -> list[Product]:
        return (
            self.db.query(Product)
            .order_by(Product.created_at.desc())
            .all()
        )

    def get_by_id(self, product_id: UUID) -> Product | None:
        return (
            self.db.query(Product)
            .filter(Product.id == product_id)
            .first()
        )


class InMemoryProductRepository(ProductRepository):

    def __init__(self):
        self._products: dict[UUID, Product] = {}
        sample = Product(
            id=uuid.uuid4(),
            name="Sample product",
            status=ProductStatus.ACTIVE,
        )
        self._products[sample.id] = sample

    def create(self, product: Product) -> Product:
        if getattr(product, "id", None) is None:
            product.id = uuid.uuid4()
        if getattr(product, "status", None) is None:
            product.status = ProductStatus.ACTIVE
        self._products[product.id] = product
        return product

    def list_all(self) -> list[Product]:
        return list(self._products.values())

    def get_by_id(self, product_id: UUID) -> Product | None:
        return self._products.get(product_id)
