from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.core.enums import ProductStatus


class ProductRead(BaseModel):
    """Response schema for product data returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str = Field(min_length=1, max_length=255)
    status: ProductStatus
