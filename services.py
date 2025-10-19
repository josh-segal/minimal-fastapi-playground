from sqlalchemy.orm import Session, selectinload, with_loader_criteria
from sqlalchemy import select
from models import Employee, Expense
from datetime import datetime


class Service:
    async def summary(
        self,
        db: Session,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ):
        query = select(Employee).options(selectinload(Employee.expenses))

        if start_date is not None and end_date is not None:
            query = query.options(
                with_loader_criteria(
                    Expense, (Expense.date >= start_date) & (Expense.date <= end_date)
                )
            )

        if start_date is not None:
            print("filtering by start_date", end_date)
            query = query.options(
                with_loader_criteria(Expense, Expense.date >= start_date)
            )

        if end_date is not None:
            print("filtering by end_date", end_date)
            query = query.options(
                with_loader_criteria(Expense, Expense.date <= end_date)
            )

        result = db.execute(query).scalars().all()

        employee_total_expenses = [  # use pydantic schema in prod
            {
                "employee_id": employee.id,
                "name": employee.name,
                "total_expenses": employee.total_expenses,
            }
            for employee in result
        ]

        return employee_total_expenses
