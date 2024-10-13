from typing import Optional
from fastapi import APIRouter
from fastapi_pagination import Page, paginate
from assignment_berkeley.operations.orders import (
    OrderResponse,
    create_order,
    get_all_orders,
    get_order_by_id,
)
from assignment_berkeley.operations.orders import OrderCreateData

router = APIRouter()


@router.post(
    "/api/orders",
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


@router.get(
    "/api/orders",
    response_model=Page[OrderResponse],
    summary="Get all orders",
    description="This endpoint retrieves all orders, optionally filtering by order status and payment status.",
)
def api_get_all_orders(
    status: Optional[str] = None,
    payment_status: Optional[str] = None,
):
    return paginate(get_all_orders(status=status, payment_status=payment_status))
