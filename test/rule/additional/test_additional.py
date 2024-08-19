from fastapi.testclient import TestClient
from sqlmodel import Session

from app.sqlmodels import OrgGroup, Taxon, AdditionalCode, AdditionalRule


class TestAdditional:
    """Tests of the public API.

    Fixtures for database and authentication come from ../conftest.py"""

    def test_additional(self, client: TestClient, session: Session):
        # Create org_group.
        org_group = OrgGroup(organisation='organisation1', group='group1')
        session.add(org_group)
        session.commit()
        session.refresh(org_group)

        # Create taxon.
        taxon = Taxon(
            name='Adalia bipunctata',
            preferred_name='Adalia bipunctata',
            search_name='adaliabipunctata',
            tvk='NBNSYS0000008319',
            preferred_tvk='NBNSYS0000008319',
            preferred=True
        )
        session.add(taxon)
        session.commit()
        session.refresh(taxon)

        # Create additional code.
        additional_code = AdditionalCode(
            code=1,
            text='Rare',
            org_group_id=org_group.id
        )
        session.add(additional_code)
        session.commit()
        session.refresh(additional_code)

        # Create additional rule.
        additional_rule = AdditionalRule(
            org_group_id=org_group.id,
            taxon_id=taxon.id,
            additional_code_id=additional_code.id
        )
        session.add(additional_rule)
        session.commit()
        session.refresh(additional_rule)

        # Request additional codes for org_group.
        response = client.get(f'/rules/additional-codes/{org_group.id}')
        assert response.status_code == 200
        result = response.json()
        assert len(result) == 1
        assert result[0]['code'] == 1
        assert result[0]['text'] == 'Rare'

        # Request additional rules for org_group.
        response = client.get(
            f'/rules/additional/org_group/{org_group.id}')
        assert response.status_code == 200
        result = response.json()
        assert len(result) == 1
        assert result[0]['tvk'] == 'NBNSYS0000008319'
        assert result[0]['taxon'] == 'Adalia bipunctata'
        assert result[0]['code'] == 1

        # Request additional rules for tvk.
        response = client.get(f'/rules/additional/tvk/{taxon.tvk}')
        assert response.status_code == 200
        result = response.json()
        assert len(result) == 1
        assert result[0]['organisation'] == 'organisation1'
        assert result[0]['group'] == 'group1'
        assert result[0]['code'] == 1
        assert result[0]['text'] == 'Rare'
