from fastapi import APIRouter
from assignment_berkeley.operations.products import ProductCreateData, create_product
from typing import Dict, Any

router = APIRouter()


@router.post(
    "/products/",
    response_model=Dict[str, Any],
    summary="Create a new product",
    description="This endpoint allows you to create a new product. You need to provide the product name, description, price, and quantity.",
)
def api_create_product(product: ProductCreateData):
    return create_product(product)
