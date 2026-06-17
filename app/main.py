from fastapi import FastAPI
from app.router import auth, car, users
from app.database import engine, Base

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(car.router)
app.include_router(users.router)