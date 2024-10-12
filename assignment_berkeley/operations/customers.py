from assignment_berkeley.db.engine import DBSession
from assignment_berkeley.db.models import DBCustomer


def read_all_customers():
    session = DBSession()
    customers = session.query(DBCustomer).all()
    return customers


def get_customer_by_id(customer_id: int):
    session = DBSession()
    customer = session.query(DBCustomer).get(customer_id)
    return customer
