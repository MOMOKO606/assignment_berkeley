from fastapi import APIRouter
from assignment_berkeley.operations.orders import create_order
from assignment_berkeley.operations.orders import OrderCreateData

router = APIRouter()


@router.post(
    "/api/orders/",
    summary="Create a new order",
    description="This endpoint allows you to create a new order. Provide customer ID and list of products with their quantities.",
)
def api_create_order(order_data: OrderCreateData):
    return create_order(order_data)
