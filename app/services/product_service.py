import json
import logging

from app.core.enums import JobStatus
from app.models.job import Job
from app.models.product import Product
from app.repositories.product_repository import ProductRepository
from app.services.agent_orchestrator import AgentOrchestrator
from app.services.job_service import JobService

logger = logging.getLogger(__name__)


class ProductService:

    def __init__(
        self,
        repository: ProductRepository,
        job_service: JobService,
        orchestrator: AgentOrchestrator,
    ):
        self.repository = repository
        self.job_service = job_service
        self.orchestrator = orchestrator

    def create_product(self, product: Product) -> Product:
        created_product = self.repository.create(product)

        job = Job(
            product_id=created_product.id,
            status=JobStatus.PENDING,
        )
        created_job = self.job_service.create_job(job)
        if not hasattr(created_product, "jobs") or created_product.jobs is None:
            created_product.jobs = []
        created_product.jobs.append(created_job)

        # Run AI enrichment pipeline
        self.orchestrator.run(created_job)

        # After pipeline completes, persist enrichment data on the product
        self._apply_enrichment(created_product, created_job)

        return created_product


    def _apply_enrichment(self, product: Product, job: Job) -> None:
        """Extract enrichment data from completed job results and persist on product."""
        result_data = getattr(job, "result_data", None)
        if not result_data:
            return

        try:
            results = json.loads(result_data)
            desc = results.get("description", {})
            vision = results.get("vision", {})
            validation = results.get("validation", {})
            emb = results.get("embedding", {})

            product.ai_title = desc.get("title")
            product.ai_description = desc.get("description")
            product.primary_color = vision.get("primary_color")
            product.category = vision.get("category")
            product.tags = json.dumps(desc.get("tags", []))
            product.quality_score = validation.get("quality_score")
            if emb.get("vector"):
                product.embedding_data = json.dumps({
                    "vector": emb.get("vector"),
                    "model_name": emb.get("model_name"),
                })

            self.repository.update(product)

            logger.info(f"Product {product.id}: Enrichment data persisted successfully")
        except Exception as e:
            logger.warning(f"Product {product.id}: Failed to apply enrichment: {e}")

    def list_products(
        self,
        limit: int = 20,
        offset: int = 0,
        category: str | None = None,
        q: str | None = None,
    ) -> dict:
        limit = min(max(1, limit), 100)
        offset = max(0, offset)
        items, total = self.repository.list_products(
            limit=limit,
            offset=offset,
            category=category,
            q=q,
        )
        return {
            "items": items,
            "total": total,
            "limit": limit,
            "offset": offset,
        }

    def get_product(self, product_id):
        return self.repository.get_by_id(product_id)

    def search_products(self, query: str, limit: int = 10) -> list[dict]:
        from app.agents.embedding_agent import EmbeddingAgent
        import numpy as np

        agent = EmbeddingAgent()
        query_res = agent.embed(query)
        q_vec = query_res.get("vector")
        q_model = query_res.get("model_name")

        if not q_vec:
            return []

        products, _ = self.repository.list_products(limit=1000, offset=0)
        results = []

        q_arr = np.array(q_vec, dtype=float)
        q_norm = np.linalg.norm(q_arr)

        for p in products:
            if not p.embedding_data:
                continue
            try:
                emb_dict = json.loads(p.embedding_data)
                p_vec = emb_dict.get("vector")
                p_model = emb_dict.get("model_name")

                # Never compare vectors from different models
                if not p_vec or p_model != q_model:
                    continue

                p_arr = np.array(p_vec, dtype=float)
                p_norm = np.linalg.norm(p_arr)

                if q_norm > 0 and p_norm > 0:
                    score = float(np.dot(q_arr, p_arr) / (q_norm * p_norm))
                else:
                    score = 0.0

                results.append({"product": p, "score": round(score, 4)})
            except Exception:
                continue

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]

    def delete_product(self, product_id: str) -> bool:
        return self.repository.delete(product_id)



