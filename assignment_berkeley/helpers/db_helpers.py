from fastapi import HTTPException
from functools import wraps
from typing import Any, Callable, TypeVar
from assignment_berkeley.db.engine import DBSession


T = TypeVar("T")


def with_session(func: Callable):
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
