from assignment_berkeley.db.engine import DBSession
from assignment_berkeley.db.models import DBProduct, to_dict
from pydantic import BaseModel
from typing import Optional


class ProductCreateData(BaseModel):
    name: str = "example_01"
    description: str = "No description provided"
    price: float = 8.99
    quantity: int = 5

    class Config:
        orm_mode = True


class ProductUpdateData(BaseModel):
    name: Optional[str] = "update_example_01"
    description: Optional[str] = "To be updated"
    price: Optional[float] = 8.99
    quantity: Optional[int] = 5

    class Config:
        orm_mode = True


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


def update_product(product_id: int, data: ProductUpdateData):
    session = DBSession()
    product = session.query(DBProduct).get(product_id)
    for key, value in data.dict(exclude_none=True).items():
        setattr(product, key, value)
    session.commit()
    return ProductResponse(**to_dict(product))


def get_product_by_id(product_id: int):
    session = DBSession()
    product = session.query(DBProduct).get(product_id)
    return product


def get_all_products():
    session = DBSession()
    products: list[DBProduct] = session.query(DBProduct).all()
    return [ProductResponse(**to_dict(product)) for product in products]
