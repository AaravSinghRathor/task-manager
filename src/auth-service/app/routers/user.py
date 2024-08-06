from typing import Annotated

from fastapi import APIRouter, Depends

from app.schemas.user import User
from app.utils.security import get_current_active_user

router = APIRouter()


@router.get("/me", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user