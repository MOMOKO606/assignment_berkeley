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


# def read_all_customers():
#     session = DBSession()
#     customers = session.query(DBCustomer).all()
#     return customers


def get_product_by_id(product_id: int):
    session = DBSession()
    product = session.query(DBProduct).get(product_id)
    return product
