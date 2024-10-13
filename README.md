# Berkeley Assignment Project

This project is a FastAPI-based web application that manages orders, products, and customers. It includes various endpoints for CRUD operations and demonstrates different coding approaches, including the use of protocols and interfaces for decoupling.

## Prerequisites

- Python 3.8+
- pipx (for installing Poetry)

## Setup

1. Install pipx if you haven't already:
   ```
   python -m pip install --user pipx
   python -m pipx ensurepath
   ```

2. Install Poetry using pipx:
   ```
   pipx install poetry
   ```

3. Clone the repository:
   ```
   git clone https://github.com/yourusername/assignment_berkeley.git
   cd assignment_berkeley
   ```

4. Install dependencies using Poetry:
   ```
   poetry install
   ```

## Running the Project

To start the FastAPI server using Poetry, run:

```
poetry run uvicorn assignment_berkeley.main:app --reload
```

The API will be available at `http://localhost:8000`.

## API Documentation

Once the server is running, you can access the interactive API documentation at:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Project Structure

```
ASSIGNMENT_BERKELEY/
│
├── .pytest_cache/
│
├── .venv/
│
├── assignment_berkeley/
│   ├── __pycache__/
│   │
│   ├── db/
│   │   ├── __pycache__/
│   │   ├── __init__.py
│   │   ├── db_interface.py
│   │   ├── engine.py
│   │   ├── models.py
│   │
│   ├── helpers/
│   │   ├── __pycache__/
│   │   ├── __init__.py
│   │   ├── product_helpers.py
│   │
│   ├── operations/
│   │   ├── __pycache__/
│   │   ├── __init__.py
│   │   ├── customers.py
│   │   ├── interface.py
│   │   ├── orders.py
│   │   ├── products.py
│   │   ├── webhooks.py
│   │
│   ├── routers/
│       ├── __pycache__/
│       ├── __init__.py
│       ├── customers.py
│       ├── orders.py
│       ├── products.py
│       ├── webhooks.py
│
├── .gitignore
├── berkeley.db
├── poetry.lock
├── pyproject.toml
├── README.md
└── tests/
    ├── __init__.py
    ├── test_api.py

```

## Special Notes

1. **Webhook Endpoint**: The webhook endpoint's full functionality is currently not available as it requires Bearer token authentication. This feature is planned for future implementation.

2. **Decoupling Demonstration**: Some endpoints in this project use protocols and interfaces for decoupling, while others do not. This is intentional to demonstrate and compare different coding approaches.

3. **Feature Branch Workflow**: During development, different branches were used for different features. Once a feature was completed, it was merged into the `develop` branch, and the `develop` branch was eventually merged into the `master` branch.