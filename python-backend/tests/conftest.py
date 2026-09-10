import os

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_fashion.db")
os.environ.pop("ANTHROPIC_API_KEY", None)  # force demo mode in tests

import pytest
from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app


@pytest.fixture(autouse=True)
def fresh_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)
