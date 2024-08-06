
from sqlalchemy import (
    Column,
    Date,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy import (
    Enum as SQLAEnum,
)
from sqlalchemy.orm import relationship

from app.enums.status_enum import Status
from app.utils.database import Base


class Task(Base):

    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(String)
    status = Column(SQLAEnum(Status))
    due_date = Column(Date)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="tasks")
