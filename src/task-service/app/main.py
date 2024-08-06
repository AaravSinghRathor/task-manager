from fastapi import FastAPI

from app.models.task import Task  # noqa: F401
from app.models.user import User  # noqa: F401
from app.routers import tasks
from app.utils.database import Base, engine
from app.utils.logger import logger
from app.utils.message_broker import close_rabbitmq_channel, get_rabbitmq_channel

app = FastAPI()


app.include_router(tasks.router, prefix="/tasks", tags=["tasks"])


@app.on_event("startup")
async def startup_event():
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize the DBs: {e}")
    try:
        get_rabbitmq_channel()
    except Exception as e:
        logger.error(f"Failed to create channel: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    try:
        close_rabbitmq_channel()
    except Exception as e:
        logger.error(f"Failed to close channel: {e}")
    logger.info("Shutdown event completed")


# if __name__ == "__main__":
#     uvicorn.run(
#         "app.main:app",
#         host="0.0.0.0",
#         port=8000,
#         log_level="debug",
#         reload=True,
#     )
