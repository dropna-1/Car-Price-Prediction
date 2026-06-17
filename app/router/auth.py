from fastapi import APIRouter, Depends, HTTPException
from app.database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from passlib.context import CryptContext
from app.models import User
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from starlette import status
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import os
import jwt

load_dotenv()

SECRET_KEY = (os.getenv("SECRET_KEY"))
ALGORITHM = "HS256"
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2 = OAuth2PasswordBearer(tokenUrl="login")

router = APIRouter(
    tags=["auth"]
)

def get_db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

db_dependency = Annotated[Session, Depends(get_db)]

class AuthRequest(BaseModel):
    username: str = Field(min_length=4, max_length=16)
    password: str = Field(min_length=8, max_length=72)

    model_config = {
        "json_schema_extra": {
            "example": {
                "username": "amir",
                "password": "12345678"
            }
        }
    }

@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, us: AuthRequest):
    user = User(username=us.username,
                hashed_password=bcrypt_context.hash(us.password))
    db.add(user)
    db.commit()

async def get_current_user(token: Annotated[str, Depends(oauth2)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
        username = payload.get("sub")
        user_id = payload.get("id")
        if username is None and user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Could not validate user")
        return {"id": user_id, "username": username}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Could not validate user")

def authenticate_user(name: str, password: str, db: db_dependency):
    user = db.query(User).filter(User.username == name).first()
    if user is None:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user

def create_access_token(username: str, user_id: int, time: timedelta):
    payload = {
        "sub": username,
        "id": user_id,
        "exp": datetime.now(timezone.utc) + time
    }
    return jwt.encode(payload, SECRET_KEY, ALGORITHM)

class Token(BaseModel):
    access_token: str
    token_type: str

@router.post("/login", response_model=Token)
async def login_for_access_token(db: db_dependency, form:
    Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = authenticate_user(form.username, form.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Could not validate user")
    token = create_access_token(user.username, user.id, timedelta(minutes=15))
    return {"access_token": token, "token_type": "bearer"}

