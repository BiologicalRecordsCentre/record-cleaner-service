from datetime import date

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.sqlmodels import OrgGroup, Taxon, TenkmRule


class TestTenkmRule:
    """Tests of the public API.

    Fixtures for database and authentication come from ../conftest.py"""

    def test_tenkm_rule(self, client: TestClient, session: Session):
        # Create org_group.
        org_group = OrgGroup(organisation='organisation1', group='group1')
        session.add(org_group)
        session.commit()
        session.refresh(org_group)

        # Create taxon.
        taxon = Taxon(
            name='Adalia bipunctata',
            tvk='NBNSYS0000008319',
            preferred_name='Adalia bipunctata',
            preferred_tvk='NBNSYS0000008319'
        )
        session.add(taxon)
        session.commit()
        session.refresh(taxon)

        # Create period rule.
        tenkm_rule = TenkmRule(
            org_group_id=org_group.id,
            taxon_id=taxon.id,
            km100='NZ',
            km10='17',
            coord_system='OSGB'
        )
        session.add(tenkm_rule)
        session.commit()
        session.refresh(tenkm_rule)

        # Request tenkm rules for org_group.
        response = client.get(
            f'/rules/tenkm/org_group/{org_group.id}')
        assert response.status_code == 200
        result = response.json()
        assert result[0]['tvk'] == 'NBNSYS0000008319'
        assert result[0]['taxon'] == 'Adalia bipunctata'
        assert result[0]['km100'] == 'NZ'
        assert result[0]['km10'] == '17'
        assert result[0]['coord_system'] == 'OSGB'

        # Request tenkm rules for tvk.
        response = client.get(f'/rules/tenkm/tvk/{taxon.tvk}')
        assert response.status_code == 200
        result = response.json()
        assert result[0]['organisation'] == 'organisation1'
        assert result[0]['group'] == 'group1'
        assert result[0]['km100'] == 'NZ'
        assert result[0]['km10'] == '17'
        assert result[0]['coord_system'] == 'OSGB'