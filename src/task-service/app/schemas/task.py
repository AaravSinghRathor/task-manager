from datetime import date

from pydantic import BaseModel

from app.enums.status_enum import Status


class TaskBase(BaseModel):
    description: str | None = None
    due_date: date | None = None


class TaskCreate(TaskBase):
    title: str


class TaskUpdatePayload(TaskBase):
    title: str | None = None
    status: Status | None = None


class Task(TaskCreate):
    id: int
    status: Status
    user_id: int

    class Config:
        ord_mode = True


class UserTasksOutput(TaskCreate):
    id: int
    status: str

    class Config:
        ord_mode = True
