from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel
from app.router.auth import get_current_user
from typing import Annotated
from starlette import status
from app.models import User
from app.database import SessionLocal
from sqlalchemy.orm import Session

router = APIRouter(
    tags=["user"]
)

def get_db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

class UserRequest(BaseModel):
    username: str
    balance: int

@router.get("/profile", status_code=status.HTTP_200_OK, response_model=UserRequest)
async def profile(db: db_dependency, user: user_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")
    return db.query(User).filter(User.id == int(user.get("id"))).first()

@router.patch("/deposit/balance", status_code=status.HTTP_200_OK)
async def deposit_balance(user: user_dependency,
                           db: db_dependency, amount: int = Query(lt=10000)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")
    current_user = db.query(User).filter(User.id == int(user.get("id"))).first()
    current_user.balance += amount
    db.commit()
    return {"balance": current_user.balance}
