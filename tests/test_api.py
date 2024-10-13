import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from assignment_berkeley.db.models import Base
from assignment_berkeley.main import app
from assignment_berkeley.db.engine import get_db

# Create a new engine instance
TEST_SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    TEST_SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create all tables in the test database
Base.metadata.create_all(bind=engine)


# Override the get_db dependency
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

# Test functions


def test_create_order():
    # First, create a customer
    customer_response = client.post(
        "/api/customers",
        json={"first_name": "John", "last_name": "Doe", "email": "john@example.com"},
    )
    assert customer_response.status_code == 200
    customer_id = customer_response.json()["id"]

    # Then, create a product
    product_response = client.post(
        "/api/products",
        json={
            "name": "Test Product",
            "description": "A test product",
            "price": 9.99,
            "quantity": 10,
        },
    )
    assert product_response.status_code == 200
    product_id = product_response.json()["id"]

    # Now, create an order
    order_response = client.post(
        "/api/orders",
        json={
            "customer_id": customer_id,
            "products": [{"product_id": product_id, "quantity": 2}],
        },
    )
    assert order_response.status_code == 200
    assert order_response.json()["customer_id"] == customer_id
    assert len(order_response.json()["products"]) == 1


def test_get_order():
    # First, create an order (reusing the create_order test)
    test_create_order()

    # Get all orders to find the ID of the created order
    all_orders_response = client.get("/api/orders")
    assert all_orders_response.status_code == 200
    orders = all_orders_response.json()["items"]
    assert len(orders) > 0
    order_id = orders[0]["id"]

    # Now, get the specific order
    order_response = client.get(f"/api/orders/{order_id}")
    assert order_response.status_code == 200
    assert order_response.json()["id"] == order_id


def test_get_all_orders():
    response = client.get("/api/orders")
    assert response.status_code == 200
    assert "items" in response.json()
    assert isinstance(response.json()["items"], list)


def test_update_order_status():
    # First, create an order (reusing the create_order test)
    test_create_order()

    # Get all orders to find the ID of the created order
    all_orders_response = client.get("/api/orders")
    assert all_orders_response.status_code == 200
    orders = all_orders_response.json()["items"]
    assert len(orders) > 0
    order_id = orders[0]["id"]

    # Update the order status
    update_response = client.put(
        f"/api/orders/{order_id}/status", json={"status": "completed"}
    )
    assert update_response.status_code == 200
    assert update_response.json()["status"] == "completed"
