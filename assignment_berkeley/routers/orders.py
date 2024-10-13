from fastapi import APIRouter
from assignment_berkeley.operations.orders import (
    OrderResponse,
    create_order,
    get_order_by_id,
)
from assignment_berkeley.operations.orders import OrderCreateData

router = APIRouter()


@router.post(
    "/api/orders/",
    summary="Create a new order",
    description="This endpoint allows you to create a new order. Provide customer ID and list of products with their quantities.",
)
def api_create_order(order_data: OrderCreateData) -> OrderResponse:
    return create_order(order_data)


@router.get(
    "/api/orders/{order_id}",
    summary="Get an order by ID",
    description="This endpoint allows you to retrieve an order using its ID. It returns the order details along with the associated products.",
    response_model=OrderResponse,
)
def api_get_order_by_id(order_id: str) -> OrderResponse:
    return get_order_by_id(order_id)
