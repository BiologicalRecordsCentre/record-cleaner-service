from fastapi.testclient import TestClient
from sqlmodel import Session

from app.sqlmodels import OrgGroup, Taxon, PhenologyRule, Stage


class TestPhenologyRule:
    """Tests of the public API.

    Fixtures for database and authentication come from ../conftest.py"""

    def test_phenology_rule(self, client: TestClient):
        # Get database connection from client.
        engine = client.app.context['engine']
        with Session(engine) as db:
            # Create org_group.
            org_group = OrgGroup(organisation='organisation1', group='group1')
            db.add(org_group)
            db.commit()

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

            # Create stage.
            stage = Stage(
                code=1,
                stage='mature',
                org_group_id=org_group.id,
                sort_order=1
            )
            db.add(stage)
            db.commit()

            # Create phenology rule.
            phenology_rule = PhenologyRule(
                org_group_id=org_group.id,
                taxon_id=taxon.id,
                stage_id=stage.id,
                start_day=8,
                start_month=6,
                end_day=6,
                end_month=10
            )
            db.add(phenology_rule)
            db.commit()

            # Request phenology rules for org_group.
            response = client.get(
                f'/rules/phenology/org_group/{org_group.id}')
            assert response.status_code == 200
            result = response.json()
            assert result == [{
                'tvk': 'NBNSYS0000008319',
                'taxon': 'Adalia bipunctata',
                'stage': 'mature',
                'start_date': '8/6',
                'end_date': '6/10'
            }]

            # Request phenology rules for tvk.
            response = client.get(f'/rules/phenology/tvk/{taxon.tvk}')
            assert response.status_code == 200
            result = response.json()
            assert result == [{
                'organisation': 'organisation1',
                'group': 'group1',
                'stage': 'mature',
                'start_date': '8/6',
                'end_date': '6/10'
            }]
