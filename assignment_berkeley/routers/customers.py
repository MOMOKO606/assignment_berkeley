from fastapi import APIRouter
from assignment_berkeley.operations.customers import read_all_customers

router = APIRouter()


@router.get("/customers")
def api_read_all_customers():
    return read_all_customers()
