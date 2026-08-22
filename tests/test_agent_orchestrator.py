import uuid
from app.core.enums import JobStatus
from app.models.job import Job
from app.repositories.job_repository import InMemoryJobRepository
from app.services.agent_orchestrator import AgentOrchestrator
from app.services.job_service import JobService


def test_agent_orchestrator_runs_complete_pipeline():
    job_repo = InMemoryJobRepository()
    job_service = JobService(job_repo)
    orchestrator = AgentOrchestrator(job_service)

    job = Job(product_id=uuid.uuid4(), status=JobStatus.PENDING)
    created_job = job_service.create_job(job)

    result_job = orchestrator.run(created_job)

    assert result_job.status == JobStatus.COMPLETED
    assert result_job.current_step == "COMPLETED"
    assert result_job.started_at is not None
    assert result_job.finished_at is not None
    assert result_job.updated_at is not None
    assert result_job.error_message is None


def test_job_service_fail_job_updates_status_and_timestamps():
    job_repo = InMemoryJobRepository()
    job_service = JobService(job_repo)

    job = Job(product_id=uuid.uuid4(), status=JobStatus.PENDING)
    created_job = job_service.create_job(job)

    failed_job = job_service.fail_job(created_job, "Processing timeout")

    assert failed_job.status == JobStatus.FAILED
    assert failed_job.error_message == "Processing timeout"
    assert failed_job.finished_at is not None
