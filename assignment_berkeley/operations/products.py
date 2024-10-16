from pydantic import BaseModel, Field, validator
from typing import Optional
from fastapi import Query
from assignment_berkeley.operations.interface import DataInterface
from assignment_berkeley.db.db_interface import DBInterface, DataObject
from assignment_berkeley.db.models import DBProduct


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
    return product_interface.update(product_id, data.dict(exclude_none=True))


def get_all_products(in_stock: bool = Query(True)):
    filter_params = {"quantity_gt": 0} if in_stock else {"quantity_lte": 0}
    return product_interface.get_all(filter_params)


def get_product_by_id(product_id: str) -> DataObject:
    return product_interface.get_by_id(product_id)


def delete_product_by_id(product_id: str) -> dict:
    return product_interface.delete(product_id)
