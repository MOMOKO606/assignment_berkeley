from fastapi import APIRouter
from assignment_berkeley.operations.customers import (
    read_all_customers,
    get_customer_by_id,
)

router = APIRouter()


@router.get("/customers")
def api_read_all_customers():
    return read_all_customers()


@router.get("/customer/{customer_id}")
def api_get_customer_by_id(customer_id: int):
    return get_customer_by_id(customer_id)
