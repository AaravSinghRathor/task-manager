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


# def reconnect_db():
#     """Recreate the engine and sessionmaker to attempt reconnection."""
#     global engine, SessionLocal
#     attempts = 5
#     for attempt in range(attempts):
#         try:
#             engine.dispose()  # Dispose of the current engine
#             engine = create_engine(
#                 SQLALCHEMY_DATABASE_URL,
#                 pool_pre_ping=True,  # Recreate the engine with pre-ping enabled
#             )
#             SessionLocal.configure(bind=engine)  # Rebind the session to the new engine
#             print("Successfully reconnected to the database.")
#             break
#         except SQLAlchemyError as e:
#             print(f"Reconnection attempt {attempt + 1}/{attempts} failed: {e}")
#             time.sleep(5)  # Wait before retrying
#     else:
#         print("Failed to reconnect to the database after multiple attempts.")
