from fastapi import APIRouter, Query
from fastapi_pagination import Page, paginate
from typing import List
from assignment_berkeley.config import logger
from assignment_berkeley.operations.products import (
    ProductCreateData,
    ProductUpdateData,
    ProductResponse,
    create_product,
    update_product,
    get_all_products,
    get_product_by_id,
    delete_product_by_id,
)


router = APIRouter()


@router.post(
    "/api/products",
    response_model=ProductResponse,
    summary="Create a new product",
    description="This endpoint allows you to create a new product. You need to provide the product name, description, price, and quantity.",
)
def api_create_product(product: ProductCreateData):
    logger.info(f"Creating product with data: {product}")
    created_product = create_product(product)
    logger.info(f"Product created successfully: {created_product}")
    return created_product


@router.put(
    "/api/products/{product_id}",
    response_model=ProductResponse,
    summary="Update an existing product by ID",
    description="This endpoint allows you to update an existing product by its ID.",
)
def api_update_product(product_id: str, product: ProductUpdateData):
    return update_product(product_id, product)


@router.get(
    "/api/products",
    response_model=Page[ProductResponse],
    summary="Retrieve all products",
    description="This endpoint allows you to retrieve a list of all products.",
)
def api_get_all_products(
    in_stock: bool = Query(True),
    # min_price: Optional[float] = Query(None, gt=0, description="Minimum price"),
    # max_price: Optional[float] = Query(None, description="Maximum price"),
):
    filter_params = {
        "quantity_gt": 0 if in_stock else float("-inf"),
        "quantity_lte": float("inf") if in_stock else 0,
        # "price_gt": min_price,
        # "price_lte": max_price,
    }
    return paginate(get_all_products(filter_params))


@router.get(
    "/api/products/{product_id}",
    response_model=ProductResponse,
    summary="Retrieve product by ID",
    description="This endpoint allows you to retrieve a product by its UUID.",
)
def api_get_product_by_id(product_id: str):
    return get_product_by_id(product_id)


@router.delete(
    "/api/products/{product_id}",
    summary="Delete a product by ID",
    description="This endpoint allows you to delete a product by its ID.",
)
def api_delete_product_by_id(product_id: str):
    return delete_product_by_id(product_id)
