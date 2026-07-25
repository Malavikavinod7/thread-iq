from app.repositories.product_repository import InMemoryProductRepository
from app.services.product_service import ProductService


def test_service_returns_products_from_repository():
    repository = InMemoryProductRepository()
    service = ProductService(repository)

    products = service.list_products()

    assert products[0].name == "Sample product"
    assert products[0].status.value == "active"
