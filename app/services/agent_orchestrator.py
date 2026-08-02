from sqlalchemy.orm import Session

from app.models.job import Job
from app.services.job_service import JobService


class AgentOrchestrator:
    """
    Coordinates the execution of AI processing steps
    for a background job.
    """

    def __init__(self, job_service: JobService):
        self.job_service = job_service

    def process_job(self, db: Session, job: Job) -> None:
        """
        Main orchestration workflow.
        """

        try:
            # Step 1
            self.job_service.mark_running(db, job)

            # Step 2
            self.run_vision_agent()

            # Step 3
            self.run_validation_engine()

            # Step 4
            self.run_description_agent()

            # Step 5
            self.run_embedding_service()

            # Finished
            self.job_service.mark_completed(db, job)

        except Exception as e:
            self.job_service.mark_failed(
                db,
                job,
                str(e),
            )

    def run_vision_agent(self):
        print("Running Vision Agent...")

    def run_validation_engine(self):
        print("Running Validation Engine...")

    def run_description_agent(self):
        print("Running Description Agent...")

    def run_embedding_service(self):
        print("Running Embedding Service...")