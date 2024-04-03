from fastapi.testclient import TestClient

from app.main import app
import app.auth as auth

client = TestClient(app)


class TestAuth:
    def test_hash_password(self):
        hashed_password = auth.hash_password("password")
        assert auth.verify_password("password", hashed_password)

    def test_token_no_user_or_password(self):
        response = client.post(
            "/token"
        )
        assert response.status_code == 422

    def test_token_no_password(self):
        response = client.post(
            "/token",
            data={"username": "johndoe"}
        )
        assert response.status_code == 422

    def test_token_no_user(self):
        response = client.post(
            "/token",
            data={"password": "secret"}
        )
        assert response.status_code == 422

    def test_token(self):
        response = client.post(
            "/token",
            data={"username": "johndoe", "password": "secret"}
        )
        assert response.status_code == 200
        json = response.json()
        assert json['token_type'] == 'bearer'
        assert auth.authenticate(json['access_token'])
