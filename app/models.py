from app.database import Base
from sqlalchemy import String, Column, Integer, ForeignKey, Boolean


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    balance = Column(Integer, default=0)
    hashed_password = Column(String)


class Car(Base):
    __tablename__ = "cars"

    id = Column(Integer, primary_key=True, index=True)
    Mileage = Column(Integer)
    Type = Column(String)
    Cylinder = Column(Integer)
    Liter = Column(Integer)
    Doors = Column(Integer)
    Sound = Column(Integer)
    Leather = Column(Integer)
    Cruise = Column(Integer)
    Price = Column(Integer)
    is_sale = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
