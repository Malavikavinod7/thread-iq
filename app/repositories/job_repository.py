import uuid
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.job import Job


class JobRepository:
    """Repository responsible only for database operations."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, job: Job) -> Job:
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def get_by_id(self, job_id: UUID) -> Job | None:
        return (
            self.db.query(Job)
            .filter(Job.id == job_id)
            .first()
        )

    def get_all(self) -> list[Job]:
        return (
            self.db.query(Job)
            .order_by(Job.created_at.desc())
            .all()
        )

    def update(self, job: Job) -> Job:
        self.db.commit()
        self.db.refresh(job)
        return job

    def delete(self, job_id: UUID) -> bool:
        job = self.get_by_id(job_id)

        if job is None:
            return False

        self.db.delete(job)
        self.db.commit()

        return True


class InMemoryJobRepository(JobRepository):

    def __init__(self):
        self._jobs: dict[UUID, Job] = {}

    def create(self, job: Job) -> Job:
        if getattr(job, "id", None) is None:
            job.id = uuid.uuid4()
        self._jobs[job.id] = job
        return job

    def get_by_id(self, job_id: UUID) -> Job | None:
        return self._jobs.get(job_id)

    def get_all(self) -> list[Job]:
        return list(self._jobs.values())

    def update(self, job: Job) -> Job:
        self._jobs[job.id] = job
        return job

    def delete(self, job_id: UUID) -> bool:
        if job_id in self._jobs:
            del self._jobs[job_id]
            return True
        return False