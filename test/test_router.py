from fastapi import status
from fastapi.testclient import TestClient


def test_read_root(client: TestClient):
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    result = response.json()
    assert result['title'] == "Record Cleaner Service"


def test_maintenance(client: TestClient):
    # Enable maintenance mode.
    response = client.post(
        '/maintenance',
        json={'mode': True, 'message': 'Service off'}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'mode': True, 'message': 'Service off'}
    # Confirm routes disabled.
    response = client.get('/users')
    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert response.json() == {'message': 'Service off'}
    # Disable maintenance mode.
    response = client.post(
        '/maintenance',
        json={'mode': False, 'message': 'Service on'}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'mode': False, 'message': 'Service on'}
    # Confirm routes enabled.
    response = client.get('/users')
    assert response.status_code == status.HTTP_200_OK
