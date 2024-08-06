from sqlalchemy.orm import Session

from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdatePayload


def get_user_tasks(
    db: Session, user_id: int, skip: int = 0, limit: int = 100
) -> list[Task]:
    return (
        db.query(Task).filter(Task.user_id == user_id).offset(skip).limit(limit).all()
    )


def get_task_by_id(db: Session, user_id: int, task_id: int) -> Task | None:
    return db.query(Task).filter(Task.user_id == user_id, Task.id == task_id).first()


def create_task(db: Session, task: TaskCreate, user_id: int) -> Task:
    db_task = Task(
        title=task.title,
        description=task.description,
        due_date=task.due_date,
        status="OPEN",
        user_id=user_id,
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


# Update an existing task
def update_task(
    db: Session, user_id: int, task_id: int, task_update_payload: TaskUpdatePayload
):
    task = get_task_by_id(db, user_id, task_id)
    if not task:
        return "task not found", None

    if task_update_payload.status:
        task.status = task_update_payload.status  # type: ignore
    if task_update_payload.title:
        task.title = task_update_payload.title  # type: ignore
    if task_update_payload.description:
        task.description = task_update_payload.description  # type: ignore
    if task_update_payload.due_date:
        task.due_date = task_update_payload.due_date  # type: ignore

    db.commit()
    db.refresh(task)
    return None, task

# mark task as completed
def mark_task_complete(db: Session, user_id: int, task_id: int):
    task = get_task_by_id(db, user_id, task_id)
    if not task:
        return "task not found", None
    task.status = "DONE" # type: ignore
    db.commit()
    db.refresh(task)
    return None, task

# Delete a task
def delete_task(db: Session, user_id: int, task_id: int) -> bool:
    task = db.query(Task).filter(Task.user_id == user_id, Task.id == task_id).first()
    if task:
        db.delete(task)
        db.commit()
        return True
    return False
