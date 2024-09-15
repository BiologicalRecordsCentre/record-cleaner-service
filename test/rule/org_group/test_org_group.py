from datetime import date

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.sqlmodels import OrgGroup


class TestOrgGroup:
    """Tests of the public API.

    Fixtures for database and authentication come from ../conftest.py"""

    def test_org_group(self, client: TestClient, db: Session):
        # Create org_group.
        org_group = OrgGroup(organisation='organisation1', group='group1')
        db.add(org_group)
        db.commit()
        db.refresh(org_group)

        # Request all org_groups.
        response = client.get('/rules/org-groups')
        assert response.status_code == 200
        result = response.json()
        assert len(result) == 1
        assert result[0]['organisation'] == 'organisation1'
        assert result[0]['group'] == 'group1'

        # Request specific org_group.
        response = client.get('/rules/org-groups/1')
        assert response.status_code == 200
        result = response.json()
        assert result['organisation'] == 'organisation1'
        assert result['group'] == 'group1'
