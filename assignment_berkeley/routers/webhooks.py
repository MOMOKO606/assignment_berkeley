from fastapi import APIRouter, HTTPException, Header
from assignment_berkeley.operations.webhooks import PaymentWebhookData, payment_webhook


router = APIRouter()


@router.post("/api/payment-webhook")
def api_payment_webhook(
    data: PaymentWebhookData,
    authorization: str = Header(...),
):
    token = authorization.split(" ")[1]  # Get token from Bearer token
    if token != "expected_token":
        raise HTTPException(status_code=403, detail="Unauthorized")
    return payment_webhook(data)
