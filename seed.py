# seed.py
from models import Employee, Expense, Base
from db import SessionLocal, engine
from datetime import datetime

# Clear the database first
print("Clearing database...")
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)
print("Database cleared and tables recreated!")

# Create database session
db = SessionLocal()

# Create employees
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
    Expense(employee_id=employees[1].id, amount=200.00, date=datetime(2025, 10, 10)),
    Expense(employee_id=employees[1].id, amount=32.50, date=datetime(2025, 10, 12)),
    # Carol's expense
    Expense(employee_id=employees[2].id, amount=67.80, date=datetime(2025, 10, 3)),
    # David's expenses
    Expense(employee_id=employees[3].id, amount=150.00, date=datetime(2025, 10, 8)),
    Expense(employee_id=employees[3].id, amount=28.90, date=datetime(2025, 10, 15)),
]

db.add_all(expenses)
db.commit()
db.close()

print("Database seeded successfully!")
