from fastapi import FastAPI
from fastapi_pagination import add_pagination
from assignment_berkeley.db.engine import init_db
from assignment_berkeley.routers import customers, products, orders, webhooks

app = FastAPI()
add_pagination(app)

DB_FILE = "sqlite:///berkeley.db"


@app.on_event("startup")
def startup_event():
    init_db(DB_FILE)


app.include_router(customers.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(webhooks.router)
