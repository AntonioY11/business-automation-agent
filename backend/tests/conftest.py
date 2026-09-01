import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.models import Base
from app.main import app, get_db
from fastapi.testclient import TestClient


TEST_DATABASE_URL = (
    "postgresql+psycopg://admin:password@localhost:5432/"
    "business_automation_test"
)

engine = create_engine(TEST_DATABASE_URL)


@pytest.fixture
def db():
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    Base.metadata.drop_all(engine)


@pytest.fixture
def client(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()