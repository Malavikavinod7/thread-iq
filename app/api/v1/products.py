from fastapi import APIRouter, status

from app.core.dependencies import ProductServiceDep
from app.schemas.product import ProductRead

router = APIRouter()


@router.get(
    "/products",
    response_model=list[ProductRead],
    status_code=status.HTTP_200_OK,
)
def list_products(service: ProductServiceDep) -> list[ProductRead]:
    """Return the list of products via the service layer dependency graph."""
    products = service.list_products()
    return [ProductRead.model_validate(product) for product in products]
