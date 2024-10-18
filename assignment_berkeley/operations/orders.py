from fastapi import HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from uuid import UUID
from assignment_berkeley.helpers.db_helpers import with_session, validate_and_get_item
from assignment_berkeley.db.db_interface import DBInterface, DataObject
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


class OrderOperations(DBInterface):
    def __init__(self):
        super().__init__(DBOrder)

    def _prepare_order_data(self, data: OrderCreateData, session) -> Dict[str, Any]:
        """准备订单数据，计算总价并验证库存"""
        customer = validate_and_get_item(session, data.customer_id, DBCustomer)
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")

        total_price = 0
        order_products = []

        for item in data.products:
            product = validate_and_get_item(session, item.product_id, DBProduct)
            if not product:
                raise HTTPException(status_code=404, detail="Product not found")
            if product.quantity < item.quantity:
                raise HTTPException(status_code=400, detail="Insufficient stock")

            total_price += product.price * item.quantity
            order_products.append(
                {
                    "product_id": UUID(item.product_id),
                    "quantity": item.quantity,
                }
            )

        return {
            "order_data": {
                "customer_id": data.customer_id,
                "total_price": total_price,
                "status": OrderStatus.pending,
                "payment_status": PaymentStatus.unpaid,
            },
            "order_products": order_products,
        }

    def _add_products_to_response(self, order_dict: Dict, session) -> OrderResponse:
        """添加产品信息到订单响应"""
        order_products = (
            session.query(order_product)
            .filter_by(order_id=UUID(order_dict["id"]))
            .all()
        )
        products = [
            OrderProductData(product_id=str(op.product_id), quantity=op.quantity)
            for op in order_products
        ]
        return OrderResponse(**order_dict, products=products)

    @with_session
    def create_order(self, data: OrderCreateData, *, session=None) -> OrderResponse:
        """使用基类的create方法创建订单"""
        prepared_data = self._prepare_order_data(data, session)
        order_dict = self.create(prepared_data["order_data"], session=session)

        # 创建订单-产品关联
        for item in prepared_data["order_products"]:
            session.execute(
                order_product.insert().values(
                    order_id=UUID(order_dict["id"]),
                    product_id=item["product_id"],
                    quantity=item["quantity"],
                )
            )

        return self._add_products_to_response(order_dict, session)

    @with_session
    def get_order_by_id(self, order_id: str, *, session=None) -> OrderResponse:
        """使用基类的get_by_id方法获取订单"""
        order_dict = self.get_by_id(order_id, session=session)
        return self._add_products_to_response(order_dict, session)

    @with_session
    def get_all_orders(
        self,
        status: Optional[str] = None,
        payment_status: Optional[str] = None,
        *,
        session=None
    ) -> List[OrderResponse]:
        """使用基类的get_all方法获取订单列表"""
        filter_params = {}
        if status:
            filter_params["status"] = status
        if payment_status:
            filter_params["payment_status"] = payment_status

        orders = self.get_all(filter_params, session=session)
        return [self._add_products_to_response(order, session) for order in orders]

    @with_session
    def update_order_status(
        self, order_id: str, data: OrderStatusUpdateData, *, session=None
    ) -> OrderResponse:
        """使用基类的update方法更新订单状态"""
        order = validate_and_get_item(session, order_id, DBOrder)
        allowed_transitions = {
            OrderStatus.pending: ["completed", "canceled"],
        }

        if data.status not in allowed_transitions.get(order.status, []):
            raise HTTPException(status_code=400, detail="Invalid status transition")
        updated_data = {"status": data.status}
        if data.status == "completed":
            updated_data["payment_status"] = "paid"
        order_dict = self.update(order_id, updated_data, session=session)
        return self._add_products_to_response(order_dict, session)
