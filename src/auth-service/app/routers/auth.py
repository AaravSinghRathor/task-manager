from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.crud.user import create_user, get_user_by_email, get_user_by_name
from app.schemas.token import Token
from app.schemas.user import UserBase, UserCreate
from app.utils.auth import create_access_token
from app.utils.database import get_db
from app.utils.security import authenticate_user

ACCESS_TOKEN_EXPIRE_MINUTES = 15
router = APIRouter()


@router.post("/login")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)],
) -> Token:
    user = get_user_by_name(db, username=form_data.username)
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@router.post("/signup", response_model=UserBase)
async def sign_up(payload: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, email=payload.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    db_user = get_user_by_name(db, username=payload.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return create_user(db, payload)
