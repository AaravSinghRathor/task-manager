import os
from typing import Any, Generator

from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from app.utils.logger import logger

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,  # Ensure the connection is valid before each use
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Dependency
def get_db() -> Generator[Session, Any, None]:
    db = SessionLocal()
    try:
        yield db
    except OperationalError as e:
        # Handle reconnection logic
        logger.error(f"Operational Error encountered: {e}")
        raise e
    finally:
        db.close()
