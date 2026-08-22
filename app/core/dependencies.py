from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.jobs.dispatcher import JobDispatcher, SyncJobDispatcher
from app.repositories.job_repository import JobRepository
from app.repositories.product_repository import (
    ProductRepository,
    SQLAlchemyProductRepository,
)
from app.services.agent_orchestrator import AgentOrchestrator
from app.services.job_service import JobService
from app.services.product_service import ProductService


def get_db() -> Generator[Session, None, None]:
    db = get_db_session()

    try:
        yield db
    finally:
        db.close()


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


def get_agent_orchestrator(
    job_service: Annotated[
        JobService,
        Depends(get_job_service),
    ],
) -> AgentOrchestrator:
    return AgentOrchestrator(job_service)


AgentOrchestratorDep = Annotated[
    AgentOrchestrator,
    Depends(get_agent_orchestrator),
]


def get_job_dispatcher(
    orchestrator: Annotated[
        AgentOrchestrator,
        Depends(get_agent_orchestrator),
    ],
) -> JobDispatcher:
    return SyncJobDispatcher(orchestrator)


JobDispatcherDep = Annotated[
    JobDispatcher,
    Depends(get_job_dispatcher),
]


def get_product_repository(
    db: Annotated[Session, Depends(get_db)],
) -> ProductRepository:
    return SQLAlchemyProductRepository(db)


def get_product_service(
    repository: Annotated[
        ProductRepository,
        Depends(get_product_repository),
    ],
    job_service: Annotated[
        JobService,
        Depends(get_job_service),
    ],
    dispatcher: Annotated[
        JobDispatcher,
        Depends(get_job_dispatcher),
    ],
) -> ProductService:
    return ProductService(
        repository=repository,
        job_service=job_service,
        dispatcher=dispatcher,
    )


ProductServiceDep = Annotated[
    ProductService,
    Depends(get_product_service),
]