from fastapi import APIRouter, status

from app.core.dependencies import ProductServiceDep
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductRead

router = APIRouter()


@router.post(
    "/products",
    response_model=ProductRead,
    status_code=status.HTTP_201_CREATED,
)
def create_product(
    payload: ProductCreate,
    service: ProductServiceDep,
):
    product = Product(
        name=payload.name,
    )

    return service.create_product(product)


@router.get(
    "/products",
    response_model=list[ProductRead],
)
def list_products(
    service: ProductServiceDep,
):
    return service.list_products()