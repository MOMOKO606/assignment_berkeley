from fastapi import HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from assignment_berkeley.helpers.db_helpers import with_session, validate_and_get_item
from assignment_berkeley.operations.interface import DataInterface
from assignment_berkeley.db.db_interface import DBOrderInterface, DataObject
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


class OrderProductData(BaseModel):
    product_id: str
    quantity: int = Field(gt=0, description="Must be greater than 0")


class OrderCreateData(BaseModel):
    customer_id: int = Field(default=1)
    products: List[OrderProductData] = [
        OrderProductData(product_id="33b2cbf1-8e62-43a8-a868-41c2c7da3061", quantity=2),
        OrderProductData(product_id="f9f70eaa-7fb6-4f9b-97c9-72b39630e8c2", quantity=3),
    ]


class OrderStatusUpdateData(BaseModel):
    status: str = Field(description="Order status (completed/canceled)")


class OrderResponse(BaseModel):
    id: str
    customer_id: int
    total_price: float
    status: str
    payment_status: str
    products: List[OrderProductData]
    created_at: str
    updated_at: str


class GetAllOrdersResponse(BaseModel):
    orders: List[OrderResponse]


class OrderOperations:
    def __init__(self):
        self.order_interface = DBOrderInterface()

    @with_session
    def create_order(self, data, *, session=None):
        # 验证客户是否存在
        customer = validate_and_get_item(session, data.customer_id, DBCustomer)
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")

        total_price = 0
        order_products = []

        # 处理每个产品的库存并计算总价
        for item in data.products:
            product = validate_and_get_item(session, item.product_id, DBProduct)
            if not product:
                raise HTTPException(status_code=404, detail="Product not found")
            if product.quantity < item.quantity:
                raise HTTPException(status_code=400, detail="Insufficient stock")

            total_price += product.price * item.quantity

            # 保存订单与产品的关联
            order_products.append(
                {
                    "product_id": UUID(item.product_id),  # 确保是UUID对象
                    "quantity": item.quantity,
                }
            )

        # 创建订单数据
        order_data = {
            "customer_id": data.customer_id,
            "total_price": total_price,
            "status": OrderStatus.pending,
            "payment_status": PaymentStatus.unpaid,
        }

        # 一次性创建订单
        order = self.order_interface.create(order_data, session=session)

        # 处理订单与产品的关联
        for item in order_products:
            self.order_interface.create_order_product(
                UUID(order["id"]),  # 确保是UUID对象
                item["product_id"],
                item["quantity"],
                session=session,
            )

        return OrderResponse(**order, products=data.products)

    @with_session
    def get_order_by_id(self, order_id: str, *, session=None) -> OrderResponse:
        order = validate_and_get_item(session, order_id, DBOrder)

        # 获取订单相关的产品
        order_products = session.query(order_product).filter_by(order_id=order.id).all()

        products = [
            OrderProductData(product_id=str(op.product_id), quantity=op.quantity)
            for op in order_products
        ]

        order_dict = to_dict(order)
        return OrderResponse(**order_dict, products=products)

    @with_session
    def get_all_orders(
        self,
        status: Optional[str] = None,
        payment_status: Optional[str] = None,
        *,
        session=None
    ) -> List[OrderResponse]:
        query = session.query(DBOrder)

        if status:
            query = query.filter(DBOrder.status == status)

        if payment_status:
            query = query.filter(DBOrder.payment_status == payment_status)

        orders = query.all()
        order_responses = []

        for order in orders:
            order_products = (
                session.query(order_product).filter_by(order_id=order.id).all()
            )
            products = [
                OrderProductData(product_id=str(op.product_id), quantity=op.quantity)
                for op in order_products
            ]

            order_dict = to_dict(order)
            order_responses.append(OrderResponse(**order_dict, products=products))

        return order_responses

    @with_session
    def update_order_status(
        self, order_id: str, data: OrderStatusUpdateData, *, session=None
    ) -> OrderResponse:
        order = validate_and_get_item(session, order_id, DBOrder)

        allowed_transitions = {
            OrderStatus.pending: ["completed", "canceled"],
        }

        current_status = order.status
        new_status = data.status

        if new_status not in allowed_transitions.get(current_status, []):
            raise HTTPException(status_code=400, detail="Invalid status transition")

        order.status = new_status

        # 获取订单相关的产品
        order_products = session.query(order_product).filter_by(order_id=order.id).all()
        products = [
            OrderProductData(product_id=str(op.product_id), quantity=op.quantity)
            for op in order_products
        ]

        order_dict = to_dict(order)
        return OrderResponse(**order_dict, products=products)
