from fastapi import APIRouter, Depends, HTTPException
from app.router.auth import get_current_user
from pydantic import BaseModel
from typing import Annotated
from starlette import status
from app.models import User, Car
from app.database import SessionLocal
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)

def get_db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.get("/", status_code=status.HTTP_200_OK)
async def list_users(db: db_dependency, user: user_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    return db.query(User).filter(User.role != "admin").all()

@router.get("/admins", status_code=status.HTTP_200_OK)
async def list_admins(db: db_dependency, user: user_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    return db.query(User).filter(User.role == "admin").all()

@router.patch("/add", status_code=status.HTTP_200_OK)
async def add_admin(db: db_dependency, user: user_dependency, user_id: int):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    db_user = db.query(User).filter(User.id == user_id).first()
    db_user.role = "admin"
    db.commit()
    return {"message": "user promoted"}

@router.delete("/del_user/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(db: db_dependency, user: user_dependency, user_id: int):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    db_user = db.query(User).filter(User.id == user_id).first()
    db.delete(db_user)
    db.commit()

@router.delete("/del_car/{car_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(db: db_dependency, user: user_dependency, car_id: int):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    car = db.query(Car).filter(Car.id == car_id).first()
    db.delete(car)
    db.commit()

class ChangePriceRequest(BaseModel):
    car_id: int
    Price: int

