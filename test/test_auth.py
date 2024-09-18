from fastapi.testclient import TestClient
from sqlmodel import Session

import app.auth as auth

from .mocks import mock_env_settings


class TestAuth:
    def test_hash_password(self):
        hashed_password = auth.hash_password("password")
        assert auth.verify_password("password", hashed_password)

    def test_token_no_user_or_password(self, client: TestClient):
        response = client.post(
            "/token"
        )
        assert response.status_code == 422

    def test_token_no_password(self, client: TestClient):
        response = client.post(
            "/token",
            data={"username": "johndoe"}
        )
        assert response.status_code == 422

    def test_token_no_user(self, client: TestClient):
        response = client.post(
            "/token",
            data={"password": "secret"}
        )
        assert response.status_code == 422

    def test_token(self, client: TestClient):
        env = mock_env_settings()
        response = client.post(
            '/token',
            data={
                'username': env.initial_user_name,
                'password': env.initial_user_pass
            }
        )
        assert response.status_code == 200
        json = response.json()
        assert json['token_type'] == 'bearer'
