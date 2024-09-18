from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.sqlmodels import User
from app.auth import get_current_admin_user, get_current_user
from app.main import app
from app.settings_env import get_env_settings
from app.user.user_repo import UserRepo

from .mocks import mock_env_settings, mock_create_db


@pytest.fixture(name="engine")
def engine_fixture():
    """Fixture which creates an in-memory SQLite database for testing."""
    return mock_create_db()


@pytest.fixture(name="db")
def session_fixture(engine) -> Generator[Session, None, None]:
    """Fixture which creates a session with the test database engine.

    Use this in tests which do not use the client-fixture."""

    with Session(engine) as session:
        env_settings = mock_env_settings()
        repo = UserRepo(session)
        repo.create_initial_user(env_settings)
        yield session


@pytest.fixture(name="client")
def client_fixture(mocker) -> Generator[TestClient, None, None]:
    """Fixture for testing API endpoints.

    This starts the app and triggers the lifespan function.
    Use client.app.context['engine'] to access the database engine
    in tests."""

    # Mock environment settings in app.main.lifespan
    mocker.patch(
        'app.main.get_env_settings',
        mock_env_settings
    )
    # Mock environment settings in app.settings
    mocker.patch(
        'app.settings.get_env_settings',
        mock_env_settings
    )

    # Mock database
    mocker.patch(
        'app.main.create_db',
        mock_create_db
    )

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
    # Override environment settings dependency.
    app.dependency_overrides[get_env_settings] = mock_env_settings

    with TestClient(app) as client:
        yield client

    # Clean up.
    app.dependency_overrides.clear()
