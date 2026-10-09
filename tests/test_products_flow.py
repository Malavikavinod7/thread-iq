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

    res = service.list_products()
    products = res["items"]

    assert products[0].name == "Sample product"
    assert products[0].status.value == "active"
    assert res["total"] == 1



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


def test_semantic_search_ranks_similar_product_higher():
    product_repo = InMemoryProductRepository()
    job_repo = InMemoryJobRepository()
    job_service = JobService(job_repo)
    orchestrator = AgentOrchestrator(job_service)
    dispatcher = SyncJobDispatcher(orchestrator)
    service = ProductService(product_repo, job_service, dispatcher)

    # Ingest two distinct products through the pipeline
    denim = service.create_product(Product(name="Navy Blue Slim Denim Jeans"))
    dress = service.create_product(Product(name="Crimson Red Evening Party Dress"))

    # Search for "denim pants"
    search_results = service.search_products("denim pants", limit=5)

    assert len(search_results) == 2
    # The denim product should rank first with a higher similarity score
    assert search_results[0]["product"].id == denim.id
    assert search_results[0]["score"] > search_results[1]["score"]

