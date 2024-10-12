from assignment_berkeley.db.engine import DBSession
from assignment_berkeley.db.models import DBProduct, to_dict
from pydantic import BaseModel
from typing import Optional
from fastapi import Query, HTTPException
from uuid import UUID


class ProductCreateData(BaseModel):
    name: str = "example_01"
    description: str = "No description provided"
    price: float = 8.99
    quantity: int = 5


class ProductUpdateData(BaseModel):
    name: Optional[str] = "update_example_01"
    description: Optional[str] = "To be updated"
    price: Optional[float] = 8.99
    quantity: Optional[int] = 5


class ProductResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    price: float
    quantity: int
    created_at: str
    updated_at: str


def create_product(data: ProductCreateData):
    session = DBSession()
    product = DBProduct(**data.dict())
    session.add(product)
    session.commit()
    return ProductResponse(**to_dict(product))


def update_product(product_id: str, data: ProductUpdateData):
    session = DBSession()
    try:
        product_id = UUID(product_id)  # Convert to UUID
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")

    product = session.query(DBProduct).filter(DBProduct.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    for key, value in data.dict(exclude_none=True).items():
        setattr(product, key, value)
    session.commit()
    return ProductResponse(**to_dict(product))


def get_all_products(in_stock: bool = Query(True)):
    session = DBSession()
    if in_stock:
        products: list[DBProduct] = (
            session.query(DBProduct).filter(DBProduct.quantity > 0).all()
        )
    else:
        products: list[DBProduct] = (
            session.query(DBProduct).filter(DBProduct.quantity <= 0).all()
        )

    return [ProductResponse(**to_dict(product)) for product in products]


def get_product_by_id(product_id: str):
    session = DBSession()
    try:
        product_uuid = UUID(product_id)  # Convert to UUID
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")

    product = session.query(DBProduct).filter(DBProduct.id == product_uuid).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    return ProductResponse(**to_dict(product))


def delete_product_by_id(product_id: str):
    session = DBSession()
    try:
        product_uuid = UUID(product_id)  # Convert to UUID
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")

    product = session.query(DBProduct).filter(DBProduct.id == product_uuid).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    session.delete(product)
    session.commit()
    return {"detail": "Product deleted successfully"}
