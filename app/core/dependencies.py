from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.repositories.product_repository import InMemoryProductRepository, ProductRepository
from app.services.product_service import ProductService


def get_db() -> Generator[Session, None, None]:
    """Create and yield a request-scoped session for dependency injection."""
    db = get_db_session()
    try:
        yield db
    finally:
        db.close()


def create_product_repository() -> ProductRepository:
    """Create the repository implementation used by the application."""
    return InMemoryProductRepository()


def get_product_repository(db: Annotated[Session, Depends(get_db)]) -> ProductRepository:
    """Create a repository bound to the current request-scoped session."""
    _ = db
    return create_product_repository()


def get_product_service(
    repository: Annotated[ProductRepository, Depends(get_product_repository)],
) -> ProductService:
    """Create the product service using the repository from the dependency graph."""
    return ProductService(repository)


ProductServiceDep = Annotated[ProductService, Depends(get_product_service)]
