from datetime import datetime, timezone
from uuid import UUID

from app.core.enums import JobStatus
from app.models.job import Job
from app.repositories.job_repository import JobRepository


class JobService:
    """
    Business logic for managing background jobs lifecycle.
    """

    def __init__(self, repository: JobRepository):
        self.repository = repository

    def create_job(self, job: Job) -> Job:
        """Create a new background job."""
        if getattr(job, "status", None) is None:
            job.status = JobStatus.PENDING
        return self.repository.create(job)

    def get_job(self, job_id: UUID | str) -> Job | None:
        """Get a job by ID."""
        if isinstance(job_id, str):
            job_id = UUID(job_id)
        return self.repository.get_by_id(job_id)

    def list_jobs(self) -> list[Job]:
        """Return all jobs."""
        return self.repository.get_all()

    def _resolve_job(self, job_or_id: Job | UUID | str) -> Job:
        """Internal helper to resolve a Job entity from an object or UUID."""
        if isinstance(job_or_id, Job):
            return job_or_id
        job = self.get_job(job_or_id)
        if job is None:
            raise ValueError(f"Job with ID '{job_or_id}' not found.")
        return job

    def start_job(self, job_or_id: Job | UUID | str) -> Job:
        """
        Transition job status to RUNNING and set started_at & updated_at timestamps.
        """
        job = self._resolve_job(job_or_id)
        now = datetime.now(timezone.utc)
        job.status = JobStatus.RUNNING
        job.started_at = now
        job.updated_at = now
        return self.repository.update(job)

    def complete_job(self, job_or_id: Job | UUID | str) -> Job:
        """
        Transition job status to COMPLETED and set finished_at & updated_at timestamps.
        """
        job = self._resolve_job(job_or_id)
        now = datetime.now(timezone.utc)
        job.status = JobStatus.COMPLETED
        job.finished_at = now
        job.updated_at = now
        return self.repository.update(job)

    def fail_job(self, job_or_id: Job | UUID | str, error_message: str) -> Job:
        """
        Transition job status to FAILED and set error_message, finished_at & updated_at timestamps.
        """
        job = self._resolve_job(job_or_id)
        now = datetime.now(timezone.utc)
        job.status = JobStatus.FAILED
        job.error_message = error_message
        job.finished_at = now
        job.updated_at = now
        return self.repository.update(job)

    def mark_running(self, job: Job) -> Job:
        return self.start_job(job)

    def mark_completed(self, job: Job) -> Job:
        return self.complete_job(job)

    def mark_failed(self, job: Job, error_message: str) -> Job:
        return self.fail_job(job, error_message)