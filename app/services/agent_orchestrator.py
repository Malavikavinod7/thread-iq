import json
import logging
from typing import Any

from app.agents.description_agent import DescriptionAgent
from app.agents.embedding_agent import EmbeddingAgent
from app.agents.validation_agent import ValidationAgent
from app.agents.vision_agent import VisionAgent
from app.models.job import Job
from app.services.job_service import JobService

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """
    Coordinates AI workflows for fashion catalog enrichment.
    Executes Vision Agent -> Description Agent -> Validation Agent -> Embedding Agent.
    """

    def __init__(
        self,
        job_service: JobService,
        vision_agent: VisionAgent | None = None,
        description_agent: DescriptionAgent | None = None,
        validation_agent: ValidationAgent | None = None,
        embedding_agent: EmbeddingAgent | None = None,
    ):
        self.job_service = job_service
        self.vision_agent = vision_agent or VisionAgent()
        self.description_agent = description_agent or DescriptionAgent()
        self.validation_agent = validation_agent or ValidationAgent()
        self.embedding_agent = embedding_agent or EmbeddingAgent()

    def run(self, job: Job) -> Job:
        """
        Main entry point to execute the multi-agent AI pipeline for a Job.
        """
        logger.info(f"Starting AgentOrchestrator workflow for Job ID: {job.id}")
        job = self.job_service.start_job(job)

        try:
            # Extract product name and image_url if available from job relation
            product_name = ""
            image_url = None
            if getattr(job, "product", None):
                if getattr(job.product, "name", None):
                    product_name = job.product.name
                if getattr(job.product, "image_url", None):
                    image_url = job.product.image_url

            # Step 1: Vision Agent
            job.current_step = "VISION_AGENT"
            logger.info(f"Job {job.id}: Executing Vision Agent")
            visual_data = self.run_vision_agent(job, product_name=product_name, image_url=image_url)

            # Step 2: Description Agent
            job.current_step = "DESCRIPTION_AGENT"
            logger.info(f"Job {job.id}: Executing Description Agent")
            description_data = self.run_description_agent(
                job, visual_data, product_name=product_name
            )

            # Step 3: Validation Agent
            job.current_step = "VALIDATION_AGENT"
            logger.info(f"Job {job.id}: Executing Validation Agent")
            validation_result = self.run_validation_agent(
                job, description_data, visual_data=visual_data
            )

            if not validation_result.get("is_valid", False):
                errors = ", ".join(validation_result.get("errors", ["Quality validation failed"]))
                raise ValueError(f"Generated title failed quality validation: {errors}")

            # Step 4: Embedding Agent
            job.current_step = "EMBEDDING_AGENT"
            logger.info(f"Job {job.id}: Executing Embedding Agent")
            embedding_result = self.run_embedding_agent(job, description_data)

            # Store all pipeline results on the job
            job.result_data = json.dumps({
                "vision": visual_data,
                "description": description_data,
                "validation": validation_result,
                "embedding": {
                    "vector": embedding_result.get("vector"),
                    "dimension": embedding_result.get("dimension"),
                    "model_name": embedding_result.get("model_name"),
                    "provider_used": embedding_result.get("provider_used"),
                },
            }, default=str)

            # Persist product enrichment directly on associated product record
            if getattr(job, "product", None):
                p = job.product
                p.ai_title = description_data.get("title")
                p.ai_description = description_data.get("description")
                p.primary_color = visual_data.get("primary_color")
                p.category = visual_data.get("category")
                p.tags = json.dumps(description_data.get("tags", []))
                p.quality_score = validation_result.get("quality_score")
                p.embedding_data = json.dumps({
                    "vector": embedding_result.get("vector"),
                    "model_name": embedding_result.get("model_name"),
                })


            # Workflow Completed
            job.current_step = "COMPLETED"
            logger.info(
                f"Job {job.id}: Workflow successfully completed with validation: "
                f"{validation_result.get('is_valid')} (Quality Score: {validation_result.get('quality_score')}, "
                f"Embedding Dim: {embedding_result.get('dimension')})"
            )
            return self.job_service.complete_job(job)


        except Exception as e:
            error_msg = f"Orchestrator failed at step '{getattr(job, 'current_step', 'UNKNOWN')}': {str(e)}"
            logger.error(f"Job {job.id}: {error_msg}", exc_info=True)
            return self.job_service.fail_job(job, error_message=error_msg)

    def run_vision_agent(
        self, job: Job, product_name: str = "", image_url: str | None = None
    ) -> dict[str, Any]:
        """Delegates feature extraction to VisionAgent."""
        logger.debug(f"Vision Agent analyzing image features for Job {job.id}...")
        return self.vision_agent.analyze(product_name=product_name, image_url=image_url)

    def run_description_agent(
        self, job: Job, visual_data: dict[str, Any], product_name: str = ""
    ) -> dict[str, Any]:
        """Delegates copy and metadata generation to DescriptionAgent."""
        logger.debug(f"Description Agent generating copy for Job {job.id} using visual inputs...")
        return self.description_agent.generate(product_name=product_name, visual_data=visual_data)

    def run_validation_agent(
        self,
        job: Job,
        description_data: dict[str, Any],
        visual_data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Delegates metadata quality and safety auditing to ValidationAgent."""
        logger.debug(f"Validation Agent auditing metadata quality for Job {job.id}...")
        result = self.validation_agent.validate(description_data, visual_data)
        if not result.get("is_valid"):
            title = description_data.get("title", "")
            if len(title) < 2:
                raise ValueError("Generated title failed quality validation minimum length requirement.")
        return result

    def run_embedding_agent(
        self, job: Job, description_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Delegates vector embedding computation to EmbeddingAgent."""
        logger.debug(f"Embedding Agent generating vector embedding for Job {job.id}...")
        text_content = (
            f"{description_data.get('title', '')} {description_data.get('description', '')}"
        )
        return self.embedding_agent.embed(text=text_content)