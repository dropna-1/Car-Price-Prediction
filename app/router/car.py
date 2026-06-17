from fastapi import APIRouter, HTTPException, Depends
from app.router.auth import get_current_user
from typing import Annotated, Literal
from app.models import Car, User
from pydantic import BaseModel, Field
from app.database import SessionLocal
from sqlalchemy.orm import Session
from starlette import status
import joblib
import pandas as pd

router = APIRouter(
    prefix="/car",
    tags = ["car"]
)

def get_db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

class CarRequest(BaseModel):
    Mileage: int
    Type: Literal["Convertible", "Coupe", "Hatchback", "Sedan", "Wegon"]
    Cylinder: int = Field(gt=4)
    Liter: int
    Doors: int = Field(gt=2)
    Cruise: int
    Sound: int
    Leather: int

    model_config = {
        "json_schema_extra": {
            "example": {
                "Mileage": 16229,
                "Type": "Sedan",
                "Cylinder": 6,
                "Liter": 3,
                "Doors": 4,
                "Cruise": 1,
                "Sound": 0,
                "Leather": 0
            }
        }
    }

@router.get("/list", status_code=status.HTTP_200_OK)
async def list_cars(db: db_dependency, user: user_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    return db.query(Car).filter(Car.owner_id == int(user.get("id"))).all()

@router.delete("/del/{car_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_car_by_id(db: db_dependency, user: user_dependency, car_id: int):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    car = db.query(Car).filter(Car.owner_id == int(user.get("id")), Car.id == car_id).first()
    if car is None:
        raise HTTPException(status_code=404, detail="Car not found")
    db.delete(car)
    db.commit()

@router.post("/", status_code=status.HTTP_201_CREATED)
async def add_car(db: db_dependency, user: user_dependency, us: CarRequest):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    data = pd.DataFrame([us.model_dump()],
    columns=["Mileage", "Type", "Cylinder", "Liter", "Doors", "Cruise", "Sound", "Leather"])
    model = joblib.load("ml/ensemble.pkl")
    y_pred = model.predict(data)

    car = Car(**us.model_dump(), Price=int(y_pred[0]), owner_id = user.get("id"))
    db.add(car)
    db.commit()
    return {"Price": int(y_pred[0])}

@router.get("/cars", status_code=status.HTTP_200_OK)
async def all_cars(db: db_dependency, user: user_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")
    current_user = db.query(User).filter(User.id == int(user.get("id"))).first()
    if current_user is None:
        raise HTTPException(status_code=404, detail="user not found")
    return db.query(Car).filter(Car.Price <= int(current_user.balance),
                                Car.owner_id != int(current_user.id)).all()

@router.post("/sale", status_code=status.HTTP_201_CREATED)
async def sale_car(db: db_dependency, user: user_dependency, car_id: int):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    current_user = db.query(User).filter(User.id == int(user.get("id"))).first()
    car = db.query(Car).filter(Car.id == car_id).first()

    if current_user.balance < car.Price or car.owner_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Insufficient balance")
    seller_user = db.query(User).filter(User.id == int(car.owner_id)).first()
    if seller_user is None:
        raise HTTPException(status_code=404, detail="seller not found")
    try:
        current_user.balance -= car.Price
        seller_user.balance += car.Price
        car.owner_id = current_user.id
        car.is_sale = True
        db.commit()
    except Exception:
        db.rollback()
        raise