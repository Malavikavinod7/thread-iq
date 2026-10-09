from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.core.enums import JobStatus


class JobCreate(BaseModel):
    product_id: str


class JobResponse(BaseModel):
    id: str
    product_id: str
    status: JobStatus

    current_step: str | None = None
    error_message: str | None = None
    result_data: str | None = None

    started_at: datetime | None = None
    finished_at: datetime | None = None

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)