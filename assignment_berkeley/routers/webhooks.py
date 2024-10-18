from fastapi import APIRouter, HTTPException, Header
from assignment_berkeley.operations.webhooks import (
    PaymentWebhookPayload,
    PaymentWebhookResponse,
    payment_webhook,
)


router = APIRouter()


@router.post("/api/payment-webhook", response_model=PaymentWebhookResponse)
async def api_payment_webhook(
    payload: PaymentWebhookPayload,
    authorization: str = Header(...),
):
    token = authorization.split(" ")[1]  # Get token from Bearer token
    if token != "expected_token":
        raise HTTPException(status_code=403, detail="Unauthorized")
    return payment_webhook(payload)
