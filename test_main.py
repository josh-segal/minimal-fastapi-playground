from fastapi.testclient import TestClient
from main import app
import pytest
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker, Session
from models import Base, Employee, Expense
from db import get_db
from datetime import datetime


def seed_data(db: Session):
    employees = [
        Employee(name="Alice Johnson", department="Engineering"),
        Employee(name="Bob Smith", department="Sales"),
        Employee(name="Carol Davis", department="Marketing"),
        Employee(name="David Chen", department="Engineering"),
        Employee(name="John Smith", department="Engineering"),
    ]

    db.add_all(employees)
    db.flush()  # Get the IDs

    # Create expenses
    expenses = [
        # Alice's expenses
        Expense(employee_id=employees[0].id, amount=45.50, date=datetime(2025, 10, 1)),
        Expense(employee_id=employees[0].id, amount=120.00, date=datetime(2025, 10, 5)),
        # Bob's expenses
        Expense(employee_id=employees[1].id, amount=85.75, date=datetime(2025, 10, 2)),
        Expense(
            employee_id=employees[1].id, amount=200.00, date=datetime(2025, 10, 10)
        ),
        Expense(employee_id=employees[1].id, amount=32.50, date=datetime(2025, 10, 12)),
        # Carol's expense
        Expense(employee_id=employees[2].id, amount=67.80, date=datetime(2025, 10, 3)),
        # David's expenses
        Expense(employee_id=employees[3].id, amount=150.00, date=datetime(2025, 10, 8)),
        Expense(employee_id=employees[3].id, amount=28.90, date=datetime(2025, 10, 15)),
    ]

    db.add_all(expenses)
    db.commit()


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    TestSessionLocal = sessionmaker(bind=engine)
    db = TestSessionLocal()
    yield db
    db.close()


@pytest.fixture(name="client")
def client_fixture(session):
    def get_db_override():
        try:
            yield session
        finally:
            pass  # session cleanup handled by session fixture

    app.dependency_overrides[get_db] = get_db_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def test_get_status(client, session):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "hello world"}


def test_summary_no_dates(client, session):
    seed_data(session)

    response = client.get("/summary")
    assert response.status_code == 200
    assert response.json() == [
        {"employee_id": 1, "name": "Alice Johnson", "total_expenses": 165.5},
        {"employee_id": 2, "name": "Bob Smith", "total_expenses": 318.25},
        {"employee_id": 3, "name": "Carol Davis", "total_expenses": 67.8},
        {"employee_id": 4, "name": "David Chen", "total_expenses": 178.9},
        {"employee_id": 5, "name": "John Smith", "total_expenses": 0},
    ]


def test_summary_start_date(client, session):
    seed_data(session)

    response = client.get("/summary?start_date=2025-10-10")
    assert response.status_code == 200
    assert response.json() == [
        {"employee_id": 1, "name": "Alice Johnson", "total_expenses": 0},
        {"employee_id": 2, "name": "Bob Smith", "total_expenses": 232.5},
        {"employee_id": 3, "name": "Carol Davis", "total_expenses": 0},
        {"employee_id": 4, "name": "David Chen", "total_expenses": 28.9},
        {"employee_id": 5, "name": "John Smith", "total_expenses": 0},
    ]


def test_summary_end_date(client, session):
    seed_data(session)

    response = client.get("/summary?end_date=2025-10-10")
    assert response.status_code == 200
    assert response.json() == [
        {"employee_id": 1, "name": "Alice Johnson", "total_expenses": 165.5},
        {"employee_id": 2, "name": "Bob Smith", "total_expenses": 285.75},
        {"employee_id": 3, "name": "Carol Davis", "total_expenses": 67.8},
        {"employee_id": 4, "name": "David Chen", "total_expenses": 150.0},
        {"employee_id": 5, "name": "John Smith", "total_expenses": 0},
    ]


def test_summary_start_date_end_date(client, session):
    seed_data(session)

    response = client.get("/summary?start_date=2025-10-10&end_date=2025-10-10")
    assert response.status_code == 200
    assert response.json() == [
        {"employee_id": 1, "name": "Alice Johnson", "total_expenses": 0},
        {"employee_id": 2, "name": "Bob Smith", "total_expenses": 200.0},
        {"employee_id": 3, "name": "Carol Davis", "total_expenses": 0},
        {"employee_id": 4, "name": "David Chen", "total_expenses": 0},
        {"employee_id": 5, "name": "John Smith", "total_expenses": 0},
    ]
