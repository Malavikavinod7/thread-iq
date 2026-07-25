from app.core.enums import ProductStatus
from app.models.product import Product


def test_product_uses_product_status_enum_for_status_field():
    status_field = Product.__table__.c.status
    assert status_field.type.python_type is ProductStatus
