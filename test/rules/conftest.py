from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import create_engine, SQLModel, Session
from sqlmodel.pool import StaticPool

import app.sqlmodels
from app.auth import authenticate
from app.database import get_db_session
from app.main import app


@pytest.fixture(name="session")
def session_fixture() -> Generator[Session, None, None]:
    """Fixture which creates an in-memory SQLite database for testing."""

    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

    # Clean up after use?


@pytest.fixture(name="client")
def client_fixture(session: Session) -> Generator[TestClient, None, None]:
    """Fixture for testing API endpoints."""

    # Override authentication to allow unauthenticated requests.
    app.dependency_overrides[authenticate] = lambda: True

    # Override database connection dependency.
    app.dependency_overrides[get_db_session] = lambda: session

    client = TestClient(app)
    yield client

    # Clean up.
    app.dependency_overrides.clear()


# @pytest.fixture(autouse=True)
# def set_rulesdir(self):
#     # Override path to rulesdir.
#     basedir = os.path.abspath(os.path.dirname(__file__))
#     rules.rulesdir = os.path.join(basedir, 'testdata')
