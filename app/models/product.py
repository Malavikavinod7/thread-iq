import uuid

from sqlalchemy import String, Float, Text, Enum as SqlAlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import ProductStatus
from app.db.base import Base
from app.models.base_mixin import TimestampMixin


class Product(TimestampMixin, Base):
    __tablename__ = "products"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[ProductStatus] = mapped_column(
        SqlAlchemyEnum(ProductStatus),
        nullable=False,
        default=ProductStatus.ACTIVE,
    )

    # AI enrichment fields (populated by the agent pipeline)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    ai_title: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    primary_color: Mapped[str | None] = mapped_column(String(100), nullable=True)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    tags: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON string
    quality_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    embedding_data: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON string {"vector": [...], "model_name": "..."}


    jobs = relationship(
        "Job",
        back_populates="product",
        cascade="all, delete-orphan",
    )

    @property
    def latest_job_id(self) -> str | None:
        if self.jobs:
            return self.jobs[-1].id
        return None