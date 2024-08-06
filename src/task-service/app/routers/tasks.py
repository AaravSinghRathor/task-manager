import json
import os
from typing import Annotated, Sequence

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    Header,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.orm import Session

from app.crud.task import (
    create_task,
    delete_task,
    get_task_by_id,
    get_user_tasks,
    mark_task_complete,
    update_task,
)
from app.schemas.task import Task, TaskCreate, TaskUpdatePayload, UserTasksOutput
from app.utils.database import get_db
from app.utils.message_broker import publish

router = APIRouter()
is_background_task_enabled = False if os.getenv("BACKGROUND_TASK_DISABLED") else True


@router.post("/", response_model=Task, status_code=status.HTTP_201_CREATED)
async def create(
    db: Annotated[Session, Depends(get_db)],
    payload: TaskCreate,
    x_user_info: Annotated[str, Header()],
    background_tasks: BackgroundTasks,
) -> Task:
    user_info = json.loads(x_user_info)
    task = create_task(db, payload, user_info["id"])
    if is_background_task_enabled:
        payload = {
            "operation": "create",
            "task": task.title,
            "email": user_info["email"],
        }  # type: ignore
        background_tasks.add_task(publish, payload)

    return task


@router.get("/{task_id}", response_model=Task)
async def get_task(
    db: Annotated[Session, Depends(get_db)],
    x_user_info: Annotated[str, Header()],
    task_id: int,
) -> Task:
    user_info = json.loads(x_user_info)
    task = get_task_by_id(db, user_info["id"], task_id)
    if not task:
        raise HTTPException(404, "task not found")
    return task


@router.get("/", response_model=list[UserTasksOutput])
async def get_tasks(
    db: Annotated[Session, Depends(get_db)],
    x_user_info: Annotated[str, Header()],
    limit: Annotated[int, Query(ge=0)] = 100,
    skip: Annotated[int, Query(ge=0)] = 0,
) -> Sequence[UserTasksOutput]:
    user_info = json.loads(x_user_info)
    tasks = get_user_tasks(db, user_info["id"], skip, limit)
    return tasks


@router.put("/{task_id}")
async def update(
    db: Annotated[Session, Depends(get_db)],
    x_user_info: Annotated[str, Header()],
    task_id: int,
    task_update_payload: TaskUpdatePayload,
    background_tasks: BackgroundTasks,
) -> Task:
    user_info = json.loads(x_user_info)
    err_msg, task = update_task(db, user_info["id"], task_id, task_update_payload)
    if not task:
        raise HTTPException(404, err_msg)
    if is_background_task_enabled:
        payload = {
            "operation": "update",
            "task": task.title,
            "email": user_info["email"],
        }
        background_tasks.add_task(publish, payload)
    return task


@router.patch("/{task_id}/complete")
async def mark_completed(
    db: Annotated[Session, Depends(get_db)],
    x_user_info: Annotated[str, Header()],
    task_id: int,
    background_tasks: BackgroundTasks,
) -> Task:
    user_info = json.loads(x_user_info)
    err_msg, task = mark_task_complete(db, user_info["id"], task_id)
    if not task:
        raise HTTPException(404, err_msg)
    if is_background_task_enabled:
        payload = {
            "operation": "complete",
            "task": task.title,
            "email": user_info["email"],
        }
        background_tasks.add_task(publish, payload)
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(
    db: Annotated[Session, Depends(get_db)],
    x_user_info: Annotated[str, Header()],
    task_id: int,
    background_tasks: BackgroundTasks,
) -> None:
    user_info = json.loads(x_user_info)
    success = delete_task(db, user_info["id"], task_id)
    if not success:
        raise HTTPException(404, "task not found")
    if is_background_task_enabled:
        payload = {"operation": "delete", "task": task_id, "email": user_info["email"]}
        background_tasks.add_task(publish, payload)
    return None
