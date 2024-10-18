from typing import Any, Dict, Type, Optional
from uuid import UUID
from fastapi import HTTPException
from sqlalchemy import and_
from assignment_berkeley.db.models import (
    Base,
    to_dict,
    order_product,
    DBProduct,
    DBOrder,
)
from assignment_berkeley.helpers.db_helpers import with_session, validate_and_get_item

DataObject = dict[str, Any]


class DBInterface:
    def __init__(self, db_class: type[Base]):
        self.db_class = db_class

    @with_session
    def get_by_id(self, id: str, *, session: Optional[Any] = None) -> DataObject:
        """通过ID获取记录"""
        if session is None:
            raise ValueError("Session is required")
        item = validate_and_get_item(session, id, self.db_class)
        return to_dict(item)

    @with_session
    def get_all(
        self, filter_params: dict = None, *, session: Optional[Any] = None
    ) -> list[DataObject]:
        if session is None:
            raise ValueError("Session is required")
        query = session.query(self.db_class)

        filters = [
            self.db_class.quantity > filter_params.get("quantity_gt", float("-inf")),
            self.db_class.quantity <= filter_params.get("quantity_lte", float("inf")),
            # self.db_class.price > filter_params.get("price_gt", 0),
            # self.db_class.price <= filter_params.get("price_lte", float("inf")),
        ]

        query = query.filter(and_(*filters))

        products = query.all()
        return [to_dict(product) for product in products]

    @with_session
    def create(self, data: DataObject, *, session: Optional[Any] = None) -> DataObject:
        if session is None:
            raise ValueError("Session is required")
        item = self.db_class(**data)
        session.add(item)
        # 强制刷新以确保获取到数据库生成的字段（如id, timestamps）
        session.flush()
        session.refresh(item)
        return to_dict(item)

    @with_session
    def update(
        self, id: str, data: DataObject, *, session: Optional[Any] = None
    ) -> DataObject:
        if session is None:
            raise ValueError("Session is required")
        item = validate_and_get_item(session, id, self.db_class)
        for key, value in data.items():
            setattr(item, key, value)
        session.flush()  # 确保更新被应用
        return to_dict(item)

    @with_session
    def delete(self, id: str, *, session: Optional[Any] = None) -> DataObject:
        """删除记录"""
        if session is None:
            raise ValueError("Session is required")
        item = validate_and_get_item(session, id, self.db_class)
        session.delete(item)
        return {"detail": "Product deleted successfully"}


class DBOrderInterface(DBInterface):
    def __init__(self):
        super().__init__(DBOrder)

    def create_order_product(self, order_id, product_id, quantity, *, session=None):
        """Insert into order_product table"""
        session.execute(
            order_product.insert().values(
                order_id=order_id, product_id=product_id, quantity=quantity
            )
        )
