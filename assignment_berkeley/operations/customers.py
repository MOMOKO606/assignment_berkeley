from typing import Optional

from pydantic import BaseModel, Field
from assignment_berkeley.db.db_interface import DBInterface, DataObject
from assignment_berkeley.db.engine import DBSession
from assignment_berkeley.db.models import DBCustomer
from assignment_berkeley.operations.interface import DataInterface


class CustomerCreateData(BaseModel):
    first_name: Optional[str] = Field("Jack", max_length=250)
    last_name: Optional[str] = Field("Treasure", max_length=250)
    email: Optional[str] = Field("jack1128@gmail.com", max_length=250)


class CustomerResponse(BaseModel):
    id: int
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[str]


# 创建 customer 的 DBInterface 实例
customer_interface: DataInterface = DBInterface(DBCustomer)


def read_all_customers():
    session = DBSession()
    customers = session.query(DBCustomer).all()
    return customers


def get_customer_by_id(customer_id: int):
    session = DBSession()
    customer = session.query(DBCustomer).get(customer_id)
    return customer


def create_customer(data: CustomerCreateData) -> DataObject:
    return customer_interface.create(data.dict(exclude_unset=True))
