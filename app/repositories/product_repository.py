import uuid
from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from app.core.enums import ProductStatus
from app.models.product import Product


class ProductRepository(ABC):

    @abstractmethod
    def create(self, product: Product) -> Product:
        ...

    @abstractmethod
    def list_products(
        self,
        limit: int = 20,
        offset: int = 0,
        category: str | None = None,
        q: str | None = None,
    ) -> tuple[list[Product], int]:
        ...

    @abstractmethod
    def get_by_id(self, product_id: str) -> Product | None:
        ...

    @abstractmethod
    def update(self, product: Product) -> Product:
        ...

    @abstractmethod
    def delete(self, product_id: str) -> bool:
        ...



class SQLAlchemyProductRepository(ProductRepository):

    def __init__(self, db: Session):
        self.db = db

    def create(self, product: Product) -> Product:
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product

    def list_products(
        self,
        limit: int = 20,
        offset: int = 0,
        category: str | None = None,
        q: str | None = None,
    ) -> tuple[list[Product], int]:
        query = self.db.query(Product)
        if category:
            query = query.filter(Product.category.ilike(f"%{category}%"))
        if q:
            query = query.filter(
                (Product.name.ilike(f"%{q}%")) | (Product.ai_title.ilike(f"%{q}%"))
            )
        total = query.count()
        items = (
            query.order_by(Product.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return items, total

    def get_by_id(self, product_id: str) -> Product | None:
        return (
            self.db.query(Product)
            .filter(Product.id == product_id)
            .first()
        )

    def update(self, product: Product) -> Product:
        self.db.commit()
        self.db.refresh(product)
        return product

    def delete(self, product_id: str) -> bool:
        product = self.get_by_id(product_id)
        if product is None:
            return False
        self.db.delete(product)
        self.db.commit()
        return True


class InMemoryProductRepository(ProductRepository):


    def __init__(self):
        self._products: dict[str, Product] = {}
        sample = Product(
            id=str(uuid.uuid4()),
            name="Sample product",
            status=ProductStatus.ACTIVE,
        )
        self._products[sample.id] = sample

    def create(self, product: Product) -> Product:
        if getattr(product, "id", None) is None:
            product.id = str(uuid.uuid4())
        if getattr(product, "status", None) is None:
            product.status = ProductStatus.ACTIVE
        self._products[product.id] = product
        return product

    def list_products(
        self,
        limit: int = 20,
        offset: int = 0,
        category: str | None = None,
        q: str | None = None,
    ) -> tuple[list[Product], int]:
        filtered = list(self._products.values())
        if category:
            filtered = [
                p for p in filtered
                if p.category and category.lower() in p.category.lower()
            ]
        if q:
            q_lower = q.lower()
            filtered = [
                p for p in filtered
                if (p.name and q_lower in p.name.lower())
                or (p.ai_title and q_lower in p.ai_title.lower())
            ]
        total = len(filtered)
        items = filtered[offset : offset + limit]
        return items, total

    def get_by_id(self, product_id: str) -> Product | None:
        return self._products.get(product_id)

    def update(self, product: Product) -> Product:
        self._products[product.id] = product
        return product

    def delete(self, product_id: str) -> bool:
        if product_id in self._products:
            del self._products[product_id]
            return True
        return False


