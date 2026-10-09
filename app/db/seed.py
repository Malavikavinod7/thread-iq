import sys
import logging
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from app.db.session import SessionLocal, create_tables
from app.repositories.product_repository import SQLAlchemyProductRepository
from app.repositories.job_repository import JobRepository
from app.services.job_service import JobService
from app.jobs.dispatcher import SyncJobDispatcher
from app.services.agent_orchestrator import AgentOrchestrator
from app.services.product_service import ProductService

from app.models.product import Product

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SEED_PRODUCTS = [
    {
        "name": "Navy Blue Slim Denim Jacket",
        "image_url": "https://images.unsplash.com/photo-1576995853123-5a10305d93c0?auto=format&fit=crop&w=800&q=80",
    },
    {
        "name": "Crimson Red Silk Evening Dress",
        "image_url": "https://images.unsplash.com/photo-1595777457583-95e059d581b8?auto=format&fit=crop&w=800&q=80",
    },
    {
        "name": "Classic Black Genuine Leather Jacket",
        "image_url": "https://images.unsplash.com/photo-1551028719-00167b16eac5?auto=format&fit=crop&w=800&q=80",
    },
    {
        "name": "100% Breathable White Cotton T-Shirt",
        "image_url": "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?auto=format&fit=crop&w=800&q=80",
    },
    {
        "name": "Emerald Green Floral Summer Dress",
        "image_url": "https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?auto=format&fit=crop&w=800&q=80",
    },
]

def seed_db():
    logger.info("Initializing database tables...")
    create_tables()

    db = SessionLocal()
    try:
        product_repo = SQLAlchemyProductRepository(db)
        job_repo = JobRepository(db)
        job_service = JobService(job_repo)
        orchestrator = AgentOrchestrator(job_service)
        dispatcher = SyncJobDispatcher(orchestrator)
        product_service = ProductService(product_repo, job_service, dispatcher)


        existing, total = product_repo.list_products(limit=10)
        if total > 0:
            logger.info(f"Database already contains {total} products. Skipping seeding.")
            return

        logger.info("Seeding initial product catalog into database...")
        for item in SEED_PRODUCTS:
            product = Product(name=item["name"], image_url=item.get("image_url"))
            created = product_service.create_product(product)
            logger.info(f"Seeded product: '{created.name}' (ID: {created.id}, Score: {created.quality_score})")

        logger.info("Seeding completed successfully!")
    finally:
        db.close()

if __name__ == "__main__":
    seed_db()
