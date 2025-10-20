from fastapi import FastAPI, APIRouter, Depends
from sqlalchemy.orm import Session
from services import Service
from datetime import datetime
from db import get_db

app = FastAPI()
service = Service()

router = APIRouter()


@router.get("/")
async def get_status():
    return {"message": "hello world"}


@router.get("/summary")
async def get_summary(
    db: Session = Depends(get_db),
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    limit: int | None = None,
    offset: int | None = None,
):
    return await service.summary(db, start_date, end_date, limit, offset)


app.include_router(router)
