from fastapi import status
from fastapi.testclient import TestClient


import app.auth as auth
from app.main import app

client = TestClient(app)

# Override authentication to allow unauthenticated requests.
app.dependency_overrides[auth.authenticate] = lambda: True


def test_read_root():
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    result = response.json()
    assert result['title'] == "Record Cleaner Service"


def test_maintenance():
    # Enable maintenance mode.
    response = client.post(
        "/maintenance",
        json={'mode': True, 'message': 'Service off'}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'mode': True, 'message': 'Service off'}
    # Confirm routes disabled.
    response = client.post("/token")
    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert response.json() == {'message': 'Service off'}
    # Disable maintenance mode.
    response = client.post(
        "/maintenance",
        json={'mode': False, 'message': 'Service on'}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'mode': False, 'message': 'Service on'}
    # Confirm routes enabled.
    response = client.post(
        "/token",
        json={'username': 'test', 'password': 'test'}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
