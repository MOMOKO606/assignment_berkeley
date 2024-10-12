from fastapi import APIRouter, Query
from typing import List
from assignment_berkeley.operations.products import (
    ProductCreateData,
    ProductUpdateData,
    ProductResponse,
    create_product,
    get_all_products,
)

router = APIRouter()


@router.post(
    "/api/products/",
    response_model=ProductResponse,
    summary="Create a new product",
    description="This endpoint allows you to create a new product. You need to provide the product name, description, price, and quantity.",
)
def api_create_product(product: ProductCreateData):
    return create_product(product)


@router.get(
    "/api/products/",
    response_model=List[ProductResponse],
    summary="Retrieve all products",
    description="This endpoint allows you to retrieve a list of all products.",
)
def api_get_all_products(in_stock: bool = Query(True)):
    return get_all_products(in_stock)


@router.put(
    "/api/products/{product_id}",
    response_model=ProductResponse,
    summary="Update the exsiting product",
    description="This endpoint allows you to update the exsiting product.",
)
def api_update_product(product_id: int, product: ProductUpdateData):
    return create_product(product_id, product)
