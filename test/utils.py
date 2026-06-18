import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.main import app
from starlette import status
from dotenv import load_dotenv
from app.models import User, Car
from app.router.auth import bcrypt_context

load_dotenv()

test_engine = create_engine(os.getenv("TEST_DATABASE_URL"))
TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

Base.metadata.create_all(bind=test_engine)

@pytest.fixture
def db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()

def override_get_current_user():
    return {"username": "amir", "id": 1, "role": "admin"}

def delete_table(table_name: str):
    with test_engine.connect() as connection:
        connection.execute(text(f"delete from {table_name};"))
        connection.commit()

@pytest.fixture
def user_test(db):
    user = User(id=1, username="amir",
                hashed_password=bcrypt_context.hash("12345678"), balance=20000)
    db.add(user)
    db.commit()
    db.refresh(user)
    yield user
    delete_table("users")

@pytest.fixture
def car_test(db):
    car = Car(id=1, Mileage=10, Type="Sedan", Cylinder=6, Liter=1,
               Doors=4, Sound=0, Leather=1, Cruise=1, Price=16655, owner_id = 1)
    db.add(car)
    db.commit()
    db.refresh(car)
    yield car
    delete_table("cars")
