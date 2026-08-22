from app.core.enums import JobStatus
from app.jobs.dispatcher import JobDispatcher
from app.models.job import Job
from app.models.product import Product
from app.repositories.product_repository import ProductRepository
from app.services.job_service import JobService


class ProductService:

    def __init__(
        self,
        repository: ProductRepository,
        job_service: JobService,
        dispatcher: JobDispatcher,
    ):
        self.repository = repository
        self.job_service = job_service
        self.dispatcher = dispatcher

    def create_product(self, product: Product) -> Product:
        created_product = self.repository.create(product)

        job = Job(
            product_id=created_product.id,
            status=JobStatus.PENDING,
        )
        created_job = self.job_service.create_job(job)

        # Dispatch job execution via JobDispatcher interface (Sync now, Celery/Redis Queue in future)
        self.dispatcher.dispatch(created_job)

        return created_product

    def list_products(self):
        return self.repository.list_all()

    def get_product(self, product_id):
        return self.repository.get_by_id(product_id)
