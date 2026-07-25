import uuid

from sqlalchemy import Column, String, Enum as SqlAlchemyEnum
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import ProductStatus
from app.db.base import Base
from app.models.base_mixin import TimestampMixin


class Product(TimestampMixin, Base):
    __tablename__ = "products"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[ProductStatus] = mapped_column(
        SqlAlchemyEnum(ProductStatus),
        nullable=False,
        default=ProductStatus.ACTIVE,
    )
