from uuid import UUID
from fastapi import HTTPException
from sqlalchemy.orm import Session
from assignment_berkeley.db.models import DBProduct


def validate_and_get_product(session: Session, product_id: str) -> DBProduct:
    try:
        product_uuid = UUID(product_id)  # Convert to UUID
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")

    product = session.query(DBProduct).filter(DBProduct.id == product_uuid).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    return product
