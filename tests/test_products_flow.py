from app.core.enums import JobStatus
from app.jobs.dispatcher import SyncJobDispatcher
from app.models.product import Product
from app.repositories.job_repository import InMemoryJobRepository
from app.repositories.product_repository import InMemoryProductRepository
from app.services.agent_orchestrator import AgentOrchestrator
from app.services.job_service import JobService
from app.services.product_service import ProductService


def test_service_returns_products_from_repository():
    product_repo = InMemoryProductRepository()
    job_repo = InMemoryJobRepository()
    job_service = JobService(job_repo)
    orchestrator = AgentOrchestrator(job_service)
    dispatcher = SyncJobDispatcher(orchestrator)
    service = ProductService(product_repo, job_service, dispatcher)

    products = service.list_products()

    assert products[0].name == "Sample product"
    assert products[0].status.value == "active"


def test_create_product_automatically_executes_orchestrator_pipeline():
    product_repo = InMemoryProductRepository()
    job_repo = InMemoryJobRepository()
    job_service = JobService(job_repo)
    orchestrator = AgentOrchestrator(job_service)
    dispatcher = SyncJobDispatcher(orchestrator)
    service = ProductService(product_repo, job_service, dispatcher)

    new_product = Product(name="New Jeans")
    created = service.create_product(new_product)

    assert created.id is not None
    jobs = job_service.list_jobs()
    assert len(jobs) == 1
    assert jobs[0].product_id == created.id
    assert jobs[0].status == JobStatus.COMPLETED
    assert jobs[0].current_step == "COMPLETED"
