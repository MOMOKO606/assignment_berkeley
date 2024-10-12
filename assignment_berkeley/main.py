from fastapi import FastAPI
from assignment_berkeley.db.engine import DBSession, init_db
from assignment_berkeley.db.models import DBCustomer

app = FastAPI()

DB_FILE = "sqlite:///berkeley.db"


@app.on_event("startup")
def startup_event():
    init_db(DB_FILE)


@app.get("/customers")
def read_all_customers():
    session = DBSession()
    customers = session.query(DBCustomer).all()
    return customers


@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}
