from typing import Any
from assignment_berkeley.db.engine import DBSession
from assignment_berkeley.db.models import Base, to_dict
from assignment_berkeley.helpers.product_helpers import validate_and_get_product

DataObject = dict[str, Any]


class DBInterface:
    def __init__(self, db_class: type[Base]):
        self.db_class = db_class

    def get_by_id(self, id: str) -> DataObject:
        session = DBSession()
        product = validate_and_get_product(session, id)
        return to_dict(product)

    def get_all(self) -> list[DataObject]: ...

    def create(self, data: DataObject) -> DataObject: ...

    def update(self, id: str, data: DataObject) -> DataObject: ...

    def delete(self, id: str) -> DataObject:
        session = DBSession()
        product = validate_and_get_product(session, id)
        session.delete(product)
        session.commit()
        return {"detail": "Product deleted successfully"}
