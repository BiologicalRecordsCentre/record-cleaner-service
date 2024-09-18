import pytest

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.auth import get_current_admin_user, get_current_user, authorization_exception
from app.settings_env import EnvSettings
from app.sqlmodels import User

from ..mocks import mock_env_settings


class TestUser:

    def test_list_users(self, client: TestClient):
        response = client.get(
            '/users'
        )
        assert response.status_code == 200
        users = response.json()
        assert len(users) == 1

        user = users[0]
        env = mock_env_settings()

        assert user['name'] == env.initial_user_name
        assert user['email'] == 'user@example.com'
        assert user['is_admin'] is True
        assert user['is_disabled'] is False

    def test_create_user(self, client: TestClient):
        response = client.post(
            '/users',
            json={
                'name': 'Rick',
                'email': 'rick@example.com',
                'password': 'pass',
                'is_admin': False,
                'is_disabled': False
            }
        )
        assert response.status_code == 200
        user = response.json()
        assert user['name'] == 'Rick'
        assert user['email'] == 'rick@example.com'
        assert user['is_admin'] is False
        assert user['is_disabled'] is False

        # Confirm user can authenticate
        response = client.post(
            '/token',
            data={
                'username': 'Rick',
                'password': 'pass'
            }
        )
        assert response.status_code == 200

    def test_get_user(self, client: TestClient):
        response = client.get('/users/root')
        assert response.status_code == 200
        user = response.json()
        assert user['name'] == 'root'
        assert user['email'] == 'user@example.com'
        assert user['is_admin'] is True
        assert user['is_disabled'] is False

    def test_update_root_user(self, client: TestClient):
        response = client.patch(
            '/users/root',
            json={
                'name': 'Rick',
                'email': 'rick@example.com',
                'password': 'pass',
                'is_admin': False,
                'is_disabled': False
            }
        )
        assert response.status_code == 403

    def test_update_user(self, client: TestClient):
        # First create user.
        response = client.post(
            '/users',
            json={
                'name': 'Rick',
                'email': 'rick@example.com',
                'password': 'pass',
                'is_admin': False,
                'is_disabled': False
            }
        )
        assert response.status_code == 200

        # Now update user.
        response = client.patch(
            '/users/Rick',
            json={
                'email': 'ricardo@example.com',
                'password': 'pass',
                'is_admin': True,
                'is_disabled': True
            }
        )
        assert response.status_code == 200
        user = response.json()
        assert user['name'] == 'Rick'
        assert user['email'] == 'ricardo@example.com'
        assert user['is_admin'] is True
        assert user['is_disabled'] is True

    def test_delete_root_user(self, client: TestClient):
        response = client.delete('/users/root')
        assert response.status_code == 403

    def test_delete_user(self, client: TestClient):
        # First create user.
        response = client.post(
            '/users',
            json={
                'name': 'Rick',
                'email': 'rick@example.com',
                'password': 'pass',
                'is_admin': False,
                'is_disabled': False
            }
        )
        assert response.status_code == 200

        # Try deleting user with wrong name.
        response = client.delete('/users/rick')
        assert response.status_code == 404

        # Now delete user.
        response = client.delete('/users/Rick')
        assert response.status_code == 200
