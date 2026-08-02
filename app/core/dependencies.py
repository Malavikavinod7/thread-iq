from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.repositories.job_repository import JobRepository
from app.repositories.product_repository import (
    ProductRepository,
    SQLAlchemyProductRepository,
)
from app.services.job_service import JobService
from app.services.product_service import ProductService


def get_db() -> Generator[Session, None, None]:
    db = get_db_session()

    try:
        yield db
    finally:
        db.close()


def get_product_repository(
    db: Annotated[Session, Depends(get_db)],
) -> ProductRepository:
    return SQLAlchemyProductRepository(db)


def get_product_service(
    repository: Annotated[
        ProductRepository,
        Depends(get_product_repository),
    ],
) -> ProductService:
    return ProductService(repository)


ProductServiceDep = Annotated[
    ProductService,
    Depends(get_product_service),
]


def get_job_repository(
    db: Annotated[Session, Depends(get_db)],
) -> JobRepository:
    return JobRepository(db)


def get_job_service(
    repository: Annotated[
        JobRepository,
        Depends(get_job_repository),
    ],
) -> JobService:
    return JobService(repository)


JobServiceDep = Annotated[
    JobService,
    Depends(get_job_service),
]