from fastapi import status
from fastapi.testclient import TestClient


def test_read_root(client: TestClient):
    # Get settings from client context.
    settings = client.app.context['settings']
    settings.db.rules_commit = 'test123'
    settings.db.rules_update_time = '2026-02-23 16:59:59'

    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    result = response.json()
    assert result['title'] == "Record Cleaner Service"
    assert result['version'] == "3.1.0"
    assert result['summary'] == "Service for checking species records against the record cleaner rules."
    assert result['contact'] == "brc@ceh.ac.uk"
    assert result['docs_url'] == "https://biologicalrecordscentre.github.io/record-cleaner-service/"
    assert result['swagger_url'] == "http://testserver/docs"
    assert result['code_repo'] == "https://github.com/BiologicalRecordsCentre/record-cleaner-service"
    assert result['rules_repo'] == settings.env.rules_repo
    assert result['rules_branch'] == settings.env.rules_branch
    assert result['rules_commit'] == 'test123'
    assert result['rules_update_time'] == '2026-02-23 16:59:59'
    assert result['maintenance_mode'] == settings.db.maintenance_mode
    assert result['maintenance_message'] == settings.db.maintenance_message


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
