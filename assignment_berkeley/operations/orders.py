from fastapi import HTTPException
from assignment_berkeley.db.engine import DBSession
from assignment_berkeley.db.models import (
    DBOrder,
    DBCustomer,
    DBProduct,
    OrderStatus,
    PaymentStatus,
    order_product,
    to_dict,
)
from assignment_berkeley.helpers.product_helpers import validate_and_get_product
from pydantic import BaseModel
from typing import List
from uuid import UUID


class OrderProductData(BaseModel):
    product_id: str
    quantity: int


class OrderCreateData(BaseModel):
    customer_id: int = 1
    products: List[OrderProductData] = [
        OrderProductData(product_id="99baee49-e3b4-4bb8-af62-92f87ca461e7", quantity=2),
        OrderProductData(product_id="f9f70eaa-7fb6-4f9b-97c9-72b39630e8c2", quantity=3),
    ]


class OrderResponse(BaseModel):
    id: str
    customer_id: int
    total_price: float
    status: str
    payment_status: str
    products: List[OrderProductData]
    created_at: str
    updated_at: str


def create_order(data: OrderCreateData) -> OrderResponse:
    session = DBSession()

    customer = session.query(DBCustomer).filter_by(id=data.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    order = DBOrder(
        customer_id=data.customer_id,
        total_price=0,
        status=OrderStatus.pending,
        payment_status=PaymentStatus.unpaid,
    )

    total_price = 0

    for item in data.products:
        product = validate_and_get_product(session, item.product_id)

        if product.quantity < item.quantity:
            raise HTTPException(
                status_code=400, detail="Insufficient stock for product"
            )

        total_price += product.price * item.quantity

        session.add(order)
        session.flush()
        session.execute(
            order_product.insert().values(
                order_id=order.id, product_id=product.id, quantity=item.quantity
            )
        )

    order.total_price = total_price

    session.add(order)
    session.commit()

    order_dict = to_dict(order)  # 使用 to_dict 将 DBOrder 转换为字典
    return OrderResponse(**order_dict, products=data.products)  # 使用解包操作符


def get_order_by_id(order_id: str) -> OrderResponse:
    session = DBSession()

    order = session.query(DBOrder).filter_by(id=UUID(order_id)).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order_products = session.query(order_product).filter_by(order_id=order.id).all()

    products = [
        {
            "product_id": str(op.product_id),
            "quantity": op.quantity,
        }
        for op in order_products
    ]

    order_dict = to_dict(order)
    order_dict["products"] = products

    return OrderResponse(**order_dict)
