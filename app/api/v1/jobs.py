from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.core.dependencies import JobServiceDep
from app.models.job import Job
from app.schemas.job import JobCreate, JobResponse

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.post("/", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job(
    payload: JobCreate,
    service: JobServiceDep,
):
    job = Job(**payload.model_dump())
    return service.create_job(job)


@router.get("/{job_id}", response_model=JobResponse)
def get_job(
    job_id: UUID,
    service: JobServiceDep,
):
    job = service.get_job(job_id)

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found",
        )

    return job


@router.get("/", response_model=list[JobResponse])
def list_jobs(
    service: JobServiceDep,
):
    return service.list_jobs()