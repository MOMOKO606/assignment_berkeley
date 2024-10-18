from uuid import UUID
from fastapi import HTTPException
from functools import wraps
from typing import Any, Callable, Dict, Type, TypeVar, Union
from sqlalchemy.orm import Session
from assignment_berkeley.db.models import DBCustomer, DBOrder, DBProduct, Base
from assignment_berkeley.db.engine import DBSession

DB_CLASS_MAPPING: Dict[Type[Base], str] = {
    DBProduct: "Product",
    DBOrder: "Order",
    DBCustomer: "Customer",
}

T = TypeVar("T")


def with_session(func: Callable) -> T:
    @wraps(func)
    def wrapper(self, *args, **kwargs) -> T:
        session = DBSession()
        kwargs["session"] = session
        try:
            result = func(self, *args, **kwargs)
            if func.__name__ in ["create", "update", "delete"]:
                session.commit()
            return result
        except Exception as e:
            if func.__name__ in ["create", "update", "delete"]:
                session.rollback()
            raise HTTPException(status_code=400, detail=str(e))
        finally:
            session.close()

    return wrapper


def validate_and_get_item(
    session: Session, id: Union[str | int], db_class: type[Base]
) -> type[Base]:
    try:
        item_primary_id = UUID(id) if isinstance(id, str) else id
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")

    item = session.query(db_class).filter(db_class.id == item_primary_id).first()
    if item is None:
        entity_name: str = DB_CLASS_MAPPING.get(db_class, "Unknown")
        raise HTTPException(status_code=404, detail=f"{entity_name} not found")

    return item
