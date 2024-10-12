from assignment_berkeley.db.engine import DBSession
from assignment_berkeley.db.models import DBProduct, to_dict
from assignment_berkeley.helpers.product_helpers import validate_and_get_product
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
    product = validate_and_get_product(session, product_id)
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
    product = validate_and_get_product(session, product_id)
    return ProductResponse(**to_dict(product))


def delete_product_by_id(product_id: str):
    session = DBSession()
    product = validate_and_get_product(session, product_id)
    session.delete(product)
    session.commit()
    return {"detail": "Product deleted successfully"}
