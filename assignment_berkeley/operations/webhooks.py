# assignment_berkeley/operations/webhook.py

from datetime import datetime
from typing import Optional
from pydantic import UUID4, BaseModel
from fastapi import HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from assignment_berkeley.db.models import DBOrder, OrderStatus, PaymentStatus
from assignment_berkeley.db.engine import DBSession
from assignment_berkeley.helpers.db_helpers import validate_and_get_item, with_session


class PaymentWebhookPayload(BaseModel):
    order_id: UUID4
    payment_status: str

    @property
    def is_valid_status(self) -> bool:
        return self.payment_status.lower() in ["paid", "failed"]


class PaymentWebhookResponse(BaseModel):
    success: bool
    message: str
    order_id: Optional[UUID4] = None
    updated_at: Optional[datetime] = None


@with_session
def payment_webhook(
    payload: PaymentWebhookPayload, *, session=None
) -> PaymentWebhookResponse:

    # 验证支付状态值
    if not payload.is_valid_status:
        raise HTTPException(
            status_code=400, detail="Invalid payment status. Must be 'paid' or 'failed'"
        )

    # 查找订单
    order = validate_and_get_item(session, payload.order_id, DBOrder)
    if not order:
        raise HTTPException(
            status_code=404, detail=f"Order with id {payload.order_id} not found"
        )

    # 验证订单当前状态是否为pending
    if order.status != OrderStatus.pending:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot update payment status for order {payload.order_id}. Order status must be 'pending'",
        )

    # 更新订单支付状态
    new_status = (
        PaymentStatus.paid
        if payload.payment_status.lower() == "paid"
        else PaymentStatus.failed
    )
    order.payment_status = new_status
    order.updated_at = datetime.utcnow()

    # 如果支付成功,更新订单状态为已完成
    if new_status == PaymentStatus.paid:
        order.status = OrderStatus.completed
    elif new_status == PaymentStatus.failed:
        order.status = OrderStatus.cancelled

    session.commit()

    return PaymentWebhookResponse(
        success=True,
        message=f"Successfully updated payment status to {new_status}",
        order_id=order.id,
        updated_at=order.updated_at,
    )
