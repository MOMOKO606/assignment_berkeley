from assignment_berkeley.db.engine import DBSession
from assignment_berkeley.db.models import DBProduct
from pydantic import BaseModel


class ProductCreateData(BaseModel):
    name: str
    description: str = None
    price: float
    quantity: int

    class Config:
        orm_mode = True


def create_product(data: ProductCreateData):
    session = DBSession()
    product = DBProduct(**data.dict())
    session.add(product)
    session.commit()
    return product


# def read_all_customers():
#     session = DBSession()
#     customers = session.query(DBCustomer).all()
#     return customers


def get_product_by_id(product_id: int):
    session = DBSession()
    product = session.query(DBProduct).get(product_id)
    return product
