from fastapi.testclient import TestClient
from sqlmodel import Session

from app.sqlmodels import OrgGroup, Taxon, TenkmRule


class TestTenkmRule:
    """Tests of the public API.

    Fixtures for database and authentication come from ../conftest.py"""

    def test_tenkm_rule(self, client: TestClient):
        # Get database connection from client.
        engine = client.app.context['engine']
        with Session(engine) as db:
            # Create org_group.
            org_group = OrgGroup(organisation='organisation1', group='group1')
            db.add(org_group)
            db.commit()
            db.refresh(org_group)

            # Create taxon.
            taxon = Taxon(
                name='Adalia bipunctata',
                preferred_name='Adalia bipunctata',
                search_name='adaliabipunctata',
                tvk='NBNSYS0000008319',
                preferred_tvk='NBNSYS0000008319',
                preferred=True,
                organism_key='NBNORG0000010513',
            )
            db.add(taxon)
            db.commit()
            db.refresh(taxon)

            # Create period rule.
            tenkm_rule = TenkmRule(
                org_group_id=org_group.id,
                organism_key=taxon.organism_key,
                taxon=taxon.name,
                km100='NZ',
                km10='17',
                coord_system='OSGB'
            )
            db.add(tenkm_rule)
            db.commit()
            db.refresh(tenkm_rule)

            # Request tenkm rules for org_group.
            response = client.get(
                f'/rules/tenkm/org_group/{org_group.id}')
            assert response.status_code == 200
            result = response.json()
            assert result[0]['organism_key'] == 'NBNORG0000010513'
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

            # Request tenkm rules for organism_key.
            response = client.get(
                f'/rules/tenkm/organism_key/{taxon.organism_key}')
            assert response.status_code == 200
            result = response.json()
            assert result[0]['organisation'] == 'organisation1'
            assert result[0]['group'] == 'group1'
            assert result[0]['km100'] == 'NZ'
            assert result[0]['km10'] == '17'
            assert result[0]['coord_system'] == 'OSGB'
