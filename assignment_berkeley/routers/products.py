from fastapi import APIRouter, Query
from fastapi_pagination import Page, paginate
from assignment_berkeley.db.db_interface import DBInterface
from assignment_berkeley.db.models import DBProduct
from typing import List
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
    "/api/products/",
    response_model=ProductResponse,
    summary="Create a new product",
    description="This endpoint allows you to create a new product. You need to provide the product name, description, price, and quantity.",
)
def api_create_product(product: ProductCreateData):
    return create_product(product)


@router.put(
    "/api/products/{product_id}",
    response_model=ProductResponse,
    summary="Update an existing product by ID",
    description="This endpoint allows you to update an existing product by its ID.",
)
def api_update_product(product_id: str, product: ProductUpdateData):
    return update_product(product_id, product)


@router.get(
    "/api/products/",
    response_model=Page[ProductResponse],
    summary="Retrieve all products",
    description="This endpoint allows you to retrieve a list of all products.",
)
def api_get_all_products(in_stock: bool = Query(True)):
    return paginate(get_all_products(in_stock))


@router.get(
    "/api/products/{product_id}",
    response_model=ProductResponse,
    summary="Retrieve product by ID",
    description="This endpoint allows you to retrieve a product by its UUID.",
)
def api_get_product_by_id(product_id: str):
    # 创建了一个包含Product数据和method的类的实例
    product_interface = DBInterface(DBProduct)
    return get_product_by_id(product_id, product_interface)


@router.delete(
    "/api/products/{product_id}",
    summary="Delete a product by ID",
    description="This endpoint allows you to delete a product by its ID.",
)
def api_delete_product_by_id(product_id: str):
    product_interface = DBInterface(DBProduct)
    return delete_product_by_id(product_id, product_interface)
