from datetime import date

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.sqlmodels import OrgGroup, Taxon, PhenologyRule, Stage, StageSynonym


class TestPhenologyRule:
    """Tests of the public API.

    Fixtures for database and authentication come from ../conftest.py"""

    def test_phenology_rule(self, client: TestClient, session: Session):
        # Create org_group.
        org_group = OrgGroup(organisation='organisation1', group='group1')
        session.add(org_group)
        session.commit()

        # Create taxon.
        taxon = Taxon(
            name='Adalia bipunctata',
            tvk='NBNSYS0000008319',
            preferred_name='Adalia bipunctata',
            preferred_tvk='NBNSYS0000008319'
        )
        session.add(taxon)
        session.commit()

        # Create stage.
        stage = Stage(
            code=1,
            stage='mature',
            org_group_id=org_group.id,
            sort_order=1
        )
        session.add(stage)
        session.commit()

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
        session.add(phenology_rule)
        session.commit()

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
