from db import Base
from sqlalchemy import Integer, Column, String, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship


class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    department = Column(String)  # this would be a fk to department table with more time

    expenses = relationship("Expense", back_populates="employee")

    @property
    def total_expenses(self) -> float:
        return sum(expense.amount for expense in self.expenses)


class Expense(Base):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    amount = Column(Float)
    date = Column(DateTime(timezone=True))

    employee = relationship("Employee", back_populates="expenses")
