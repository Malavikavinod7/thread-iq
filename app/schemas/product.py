from pydantic import BaseModel, ConfigDict, Field

from app.core.enums import ProductStatus


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    image_url: str | None = Field(None, max_length=500)


class ProductRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    image_url: str | None = None
    status: ProductStatus

    # AI enrichment fields
    ai_title: str | None = None
    ai_description: str | None = None
    primary_color: str | None = None
    category: str | None = None
    tags: str | None = None
    quality_score: float | None = None
    latest_job_id: str | None = None



class PaginatedProducts(BaseModel):
    items: list[ProductRead]
    total: int
    limit: int
    offset: int


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    limit: int = Field(10, ge=1, le=50)


class SearchResultItem(BaseModel):
    product: ProductRead
    score: float