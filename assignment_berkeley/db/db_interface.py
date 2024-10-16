from typing import Any, Optional
from fastapi import HTTPException
from assignment_berkeley.db.models import Base, to_dict
from assignment_berkeley.helpers.product_helpers import validate_and_get_product
from assignment_berkeley.helpers.db_helpers import with_session

DataObject = dict[str, Any]


class DBInterface:
    def __init__(self, db_class: type[Base]):
        self.db_class = db_class

    @with_session
    def get_by_id(self, id: str, *, session: Optional[Any] = None) -> DataObject:
        """通过ID获取记录"""
        if session is None:
            raise ValueError("Session is required")
        product = validate_and_get_product(session, id)
        return to_dict(product)

    @with_session
    def get_all(
        self, filter_params: dict = None, *, session: Optional[Any] = None
    ) -> list[DataObject]:
        if session is None:
            raise ValueError("Session is required")
        query = session.query(self.db_class)

        if filter_params:
            if "quantity_gt" in filter_params:
                query = query.filter(
                    self.db_class.quantity > filter_params["quantity_gt"]
                )
            elif "quantity_lte" in filter_params:
                query = query.filter(
                    self.db_class.quantity <= filter_params["quantity_lte"]
                )

        products = query.all()
        return [to_dict(product) for product in products]

    @with_session
    def create(self, data: DataObject, *, session: Optional[Any] = None) -> DataObject:
        if session is None:
            raise ValueError("Session is required")
        product = self.db_class(**data)
        session.add(product)
        # 强制刷新以确保获取到数据库生成的字段（如id, timestamps）
        session.flush()
        session.refresh(product)
        return to_dict(product)

    @with_session
    def update(
        self, id: str, data: DataObject, *, session: Optional[Any] = None
    ) -> DataObject:
        if session is None:
            raise ValueError("Session is required")
        product = validate_and_get_product(session, id)
        for key, value in data.items():
            setattr(product, key, value)
        session.flush()  # 确保更新被应用
        return to_dict(product)

    @with_session
    def delete(self, id: str, *, session: Optional[Any] = None) -> DataObject:
        """删除记录"""
        if session is None:
            raise ValueError("Session is required")
        product = validate_and_get_product(session, id)
        session.delete(product)
        return {"detail": "Product deleted successfully"}
