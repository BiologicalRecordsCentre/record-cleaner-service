from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import create_engine, SQLModel, Session
from sqlmodel.pool import StaticPool

from app.sqlmodels import User
from app.auth import get_current_admin_user, get_current_user
from app.database import get_db_session
from app.main import app
from app.user.user_repo import UserRepo


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
        repo = UserRepo(session)
        repo.create_initial_user()
        yield session

    # Clean up after use?


@pytest.fixture(name="client")
def client_fixture(session: Session) -> Generator[TestClient, None, None]:
    """Fixture for testing API endpoints."""

    # Override authentication to allow admin requests.
    app.dependency_overrides[get_current_admin_user] = lambda: User(
        name='Fred',
        email='fred@fred.com',
        hash='abc',
        is_admin=True,
        is_disabled=False
    )
    # Override authentication to allow user requests.
    app.dependency_overrides[get_current_user] = lambda: User(
        name='Tom',
        email='tom@tom.com',
        hash='abc',
        is_admin=False,
        is_disabled=False
    )
    # Override database connection dependency.
    app.dependency_overrides[get_db_session] = lambda: session

    client = TestClient(app)
    yield client

    # Clean up.
    app.dependency_overrides.clear()
