from fastapi import APIRouter, HTTPException, Query, status

from app.core.dependencies import ProductServiceDep
from app.models.product import Product
from app.schemas.product import (
    PaginatedProducts,
    ProductCreate,
    ProductRead,
    SearchRequest,
    SearchResultItem,
)

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
        image_url=payload.image_url,
    )

    return service.create_product(product)


@router.get(
    "/products",
    response_model=PaginatedProducts,
)
def list_products(
    service: ProductServiceDep,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    category: str | None = Query(None),
    q: str | None = Query(None),
):
    return service.list_products(limit=limit, offset=offset, category=category, q=q)


@router.post(
    "/products/search",
    response_model=list[SearchResultItem],
)
def search_products(
    payload: SearchRequest,
    service: ProductServiceDep,
):
    return service.search_products(query=payload.query, limit=payload.limit)


@router.get(
    "/products/{product_id}",
    response_model=ProductRead,
)
def get_product(
    product_id: str,
    service: ProductServiceDep,
):
    product = service.get_product(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.delete(
    "/products/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_product(
    product_id: str,
    service: ProductServiceDep,
):
    success = service.delete_product(product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Product not found")
    return None