from uuid import UUID

from app.core.enums import JobStatus
from app.models.job import Job
from app.repositories.job_repository import JobRepository


class JobService:
    """
    Business logic for managing background jobs.
    """

    def __init__(self, repository: JobRepository):
        self.repository = repository

    def create_job(self, job: Job) -> Job:
        """
        Create a new background job.
        """
        return self.repository.create(job)

    def get_job(self, job_id: UUID) -> Job | None:
        """
        Get a job by ID.
        """
        return self.repository.get_by_id(job_id)

    def list_jobs(self) -> list[Job]:
        """
        Return all jobs.
        """
        return self.repository.get_all()

    def mark_running(self, job: Job) -> Job:
        """
        Mark a job as RUNNING.
        """
        job.status = JobStatus.RUNNING
        return self.repository.update(job)

    def mark_completed(self, job: Job) -> Job:
        """
        Mark a job as COMPLETED.
        """
        job.status = JobStatus.SUCCESS
        return self.repository.update(job)

    def mark_failed(
        self,
        job: Job,
        error_message: str,
    ) -> Job:
        """
        Mark a job as FAILED.
        """
        job.status = JobStatus.FAILED
        job.error_message = error_message
        return self.repository.update(job)