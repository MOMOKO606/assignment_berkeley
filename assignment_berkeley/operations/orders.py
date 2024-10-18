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


def get_order_by_id(order_id: str) -> DataObject:
    return order_interface.get_by_id(order_id)


def get_all_orders(
    status: Optional[str] = None, payment_status: Optional[str] = None
) -> List[OrderResponse]:
    session = DBSession()

    query = session.query(DBOrder)

    if status:
        query = query.filter(DBOrder.status == status)

    if payment_status:
        query = query.filter(DBOrder.payment_status == payment_status)

    orders = query.all()

    order_responses = []
    for order in orders:
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
        order_responses.append(OrderResponse(**order_dict))

    return order_responses


def update_order_status(order_id: str, data: OrderStatusUpdateData) -> OrderResponse:
    session = DBSession()

    order = session.query(DBOrder).filter_by(id=UUID(order_id)).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    allowed_transitions = {
        OrderStatus.pending: ["completed", "canceled"],
    }

    current_status = order.status
    new_status = data.status

    if new_status not in allowed_transitions.get(current_status, []):
        raise HTTPException(status_code=400, detail="Invalid status transition")

    order.status = new_status

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

    session.commit()

    return OrderResponse(**order_dict)
