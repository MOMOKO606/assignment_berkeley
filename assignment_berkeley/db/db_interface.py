from typing import Any

from fastapi import HTTPException
from assignment_berkeley.db.engine import DBSession
from assignment_berkeley.db.models import Base, to_dict
from assignment_berkeley.helpers.product_helpers import validate_and_get_product

DataObject = dict[str, Any]


class DBInterface:
    def __init__(self, db_class: type[Base]):
        self.db_class = db_class

    def get_by_id(self, id: str) -> DataObject:
        session = DBSession()
        try:
            product = validate_and_get_product(session, id)
            return to_dict(product)
        finally:
            session.close()

    def get_all(self, filter_params: dict = None) -> list[DataObject]:
        session = DBSession()
        try:
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
        finally:
            session.close()

    def create(self, data: DataObject) -> DataObject:
        session = DBSession()
        try:
            product = self.db_class(**data)
            session.add(product)
            session.commit()
            return to_dict(product)
        except Exception as e:
            session.rollback()
            raise HTTPException(status_code=400, detail=str(e))
        finally:
            session.close()

    def update(self, id: str, data: DataObject) -> DataObject:
        session = DBSession()
        try:
            product = validate_and_get_product(session, id)
            for key, value in data.items():
                setattr(product, key, value)
            session.commit()
            return to_dict(product)
        except Exception as e:
            session.rollback()
            raise HTTPException(status_code=400, detail=str(e))
        finally:
            session.close()

    def delete(self, id: str) -> DataObject:
        session = DBSession()
        try:
            product = validate_and_get_product(session, id)
            session.delete(product)
            session.commit()
            return {"detail": "Product deleted successfully"}
        except Exception as e:
            session.rollback()
            raise HTTPException(status_code=400, detail=str(e))
        finally:
            session.close()
