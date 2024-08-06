import json

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.models.task import Task
from app.utils.database import Base, get_db

# Setup the in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)
user_info = {"id": 1, "email": "test@gmail.com"}
x_user_info_header = {"X-User-Info": json.dumps(user_info)}


def test_get_task_by_id():
    response = client.get("/tasks/1", headers=x_user_info_header)

    assert response.status_code == 200, response.text
    data = response.json()

    assert "id" in data and data["id"] == 1
    assert "title" in data and data["title"] == "Task Test"
    assert "status" in data and data["status"] == "OPEN"
    assert "description" in data and data["description"] == "Task Test Description"
    assert "user_id" in data and data["user_id"] == 1


def test_get_user_tasks():
    response = client.get("/tasks/", headers=x_user_info_header)

    assert response.status_code == 200, response.text
    data = response.json()[0]

    assert "id" in data and data["id"] == 1
    assert "title" in data and data["title"] == "Task Test"
    assert "status" in data and data["status"] == "OPEN"
    assert "description" in data and data["description"] == "Task Test Description"


def test_update_task():
    request_body = {
        "title": "Task Test 2",
        "description": "Task Test Description 2",
        "status": "IN PROGRESS",
    }

    response = client.put("/tasks/1", headers=x_user_info_header, json=request_body)
    assert response.status_code == 200, response.text

    response = client.get("tasks/1", headers=x_user_info_header)
    assert response.status_code == 200, response.text

    data = response.json()
    assert "id" in data and data["id"] == 1
    assert "title" in data and data["title"] == "Task Test 2"
    assert "status" in data and data["status"] == "IN PROGRESS"
    assert "description" in data and data["description"] == "Task Test Description 2"


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    # Create the tables in the test database
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    task = Task(
        title="Task Test",
        description="Task Test Description",
        status="OPEN",
        user_id=1,
    )
    session.add(task)
    session.commit()
    session.close()
    yield
    # Drop the tables in the test database
    Base.metadata.drop_all(bind=engine)

