from assignment_berkeley.db.engine import DBSession
from assignment_berkeley.db.models import DBCustomer


def read_all_customers():
    session = DBSession()
    customers = session.query(DBCustomer).all()
    return customers
