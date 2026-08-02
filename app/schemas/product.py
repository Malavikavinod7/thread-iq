from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.core.enums import ProductStatus


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)


class ProductRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    status: ProductStatus