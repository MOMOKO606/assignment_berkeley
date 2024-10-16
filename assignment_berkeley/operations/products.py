from assignment_berkeley.db.engine import DBSession
from assignment_berkeley.db.models import DBProduct, to_dict
from assignment_berkeley.helpers.product_helpers import validate_and_get_product
from pydantic import BaseModel, Field, validator
from typing import Optional
from fastapi import Query, HTTPException
from uuid import UUID

from assignment_berkeley.operations.interface import DataInterface
from assignment_berkeley.db.db_interface import DBInterface, DataObject


class ProductCreateData(BaseModel):
    name: str = Field(default="example_01")
    description: str = Field(default="No description provided")
    price: float = Field(default=8.99, gt=0, description="Must be greater than 0")
    quantity: int = Field(default=5, gt=0, description="Must be greater than 0")

    @validator("price", "quantity")
    def check_positive(cls, value):
        if value <= 0:
            raise ValueError("Must be greater than 0")
        return value


class ProductUpdateData(BaseModel):
    name: Optional[str] = Field(default="update_example_01")
    description: Optional[str] = Field(default="To be updated")
    price: Optional[float] = Field(
        default=8.99, gt=0, description="Must be greater than 0"
    )
    quantity: Optional[int] = Field(
        default=5, gt=0, description="Must be greater than 0"
    )

    @validator("price", "quantity", pre=True, always=True)
    def check_positive_optional(cls, value):
        if value is not None and value <= 0:
            raise ValueError("Must be greater than 0")
        return value


class ProductResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    price: float
    quantity: int
    created_at: str
    updated_at: str


# Create an instance of DBInterface where contains the CRUD methods
# The pass-in argument is the DBProduct
product_interface: DataInterface = DBInterface(DBProduct)


def create_product(data: ProductCreateData):
    return product_interface.create(data.dict())


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


def get_product_by_id(product_id: str) -> DataObject:
    return product_interface.get_by_id(product_id)


def delete_product_by_id(product_id: str) -> dict:
    return product_interface.delete(product_id)
