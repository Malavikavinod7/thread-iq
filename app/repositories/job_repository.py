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