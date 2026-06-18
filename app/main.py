from fastapi import FastAPI
from app.router import auth, car, user, admin
from app.database import engine, Base, SessionLocal
from contextlib import asynccontextmanager
from app.models import User

@asynccontextmanager
async def lifespan(api: FastAPI):
    with SessionLocal() as db:
        ad = db.query(User).filter(User.role == "admin").first()
        if ad is None:
            ad = User(username="admin",
                      hashed_password=auth.bcrypt_context.hash("1234"), role="admin")
            db.add(ad)
            db.commit()
    try:
        yield
    finally:
        pass

app = FastAPI(lifespan=lifespan)

Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(car.router)
app.include_router(user.router)
app.include_router(admin.router)