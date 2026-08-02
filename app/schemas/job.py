from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.core.enums import JobStatus


class JobCreate(BaseModel):
    product_id: UUID


class JobResponse(BaseModel):
    id: UUID
    product_id: UUID
    status: JobStatus

    current_step: str | None = None
    error_message: str | None = None

    started_at: datetime | None = None
    finished_at: datetime | None = None

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)