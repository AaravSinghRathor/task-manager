from pydantic import BaseModel


class UserBase(BaseModel):
    email: str
    username: str


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    disabled: bool


class User(UserBase):
    id: int
    disabled: bool

    class Config:
        orm_mode = True


class UserInDB(User):
    password: str
