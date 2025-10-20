from sqlalchemy.orm import Session, selectinload, with_loader_criteria
from sqlalchemy import select
from models import Employee, Expense
from datetime import datetime, timedelta


class Service:
    def __init__(self, cache_ttl=60):
        self._cache = {}
        self._cache_ttl = timedelta(seconds=cache_ttl)

    async def summary(
        self,
        db: Session,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ):
        query = select(Employee).options(selectinload(Employee.expenses))

        if start_date is not None and end_date is not None:
            query = query.options(
                with_loader_criteria(
                    Expense, (Expense.date >= start_date) & (Expense.date <= end_date)
                )
            )

        if start_date is not None:
            print("filtering by start_date", start_date)
            query = query.options(
                with_loader_criteria(Expense, Expense.date >= start_date)
            )

        if end_date is not None:
            print("filtering by end_date", end_date)
            query = query.options(
                with_loader_criteria(Expense, Expense.date <= end_date)
            )

        if limit is not None:
            query = query.limit(limit)

        if offset is not None:
            query = query.offset(offset)

        key = (start_date, end_date, limit, offset)
        if key in self._cache:
            cache_data, cache_time = self._cache[key]
            if datetime.now() - cache_time < self._cache_ttl:
                print("calling cache")
                return cache_data

        result = db.execute(query).scalars().all()

        employee_total_expenses = [  # use pydantic schema in prod
            {
                "employee_id": employee.id,
                "name": employee.name,
                "total_expenses": employee.total_expenses,
            }
            for employee in result
        ]

        self._cache[key] = (employee_total_expenses, datetime.now())

        return employee_total_expenses
