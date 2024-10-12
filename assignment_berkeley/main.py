from fastapi import FastAPI
from assignment_berkeley.db.engine import init_db
from assignment_berkeley.routers import customers

app = FastAPI()

DB_FILE = "sqlite:///berkeley.db"


@app.on_event("startup")
def startup_event():
    init_db(DB_FILE)


app.include_router(customers.router)


@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}
