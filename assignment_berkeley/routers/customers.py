from fastapi import APIRouter
from assignment_berkeley.operations.customers import (
    CustomerCreateData,
    CustomerResponse,
    create_customer,
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


@router.post(
    "/customers",
    response_model=CustomerResponse,
    summary="Create a new customer",
    description="Create a new customer with the provided information.",
)
def api_create_customer(customer: CustomerCreateData):
    return create_customer(customer)
