# assignment_berkeley/operations/webhook.py

from pydantic import BaseModel
from fastapi import HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from assignment_berkeley.db.models import DBOrder
from assignment_berkeley.db.engine import DBSession


class PaymentWebhookData(BaseModel):
    order_id: str
    payment_status: str


def payment_webhook(data: PaymentWebhookData):
    session = DBSession()

    order = session.query(DBOrder).filter_by(id=data.order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.status != OrderStatus.pending:
        raise HTTPException(
            status_code=400, detail="Order status not allowed for update"
        )

    if data.payment_status not in ["paid", "failed"]:
        raise HTTPException(status_code=400, detail="Invalid payment status")

    order.payment_status = data.payment_status
    session.commit()

    return {
        "message": "Payment status updated successfully",
        "order_id": str(order.id),
        "payment_status": order.payment_status,
    }
