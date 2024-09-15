from datetime import date

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.sqlmodels import OrgGroup, Taxon, PeriodRule


class TestPeriodRule:
    """Tests of the public API.

    Fixtures for database and authentication come from ../conftest.py"""

    def test_period_rule(self, client: TestClient, db: Session):
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
            preferred=True
        )
        db.add(taxon)
        db.commit()
        db.refresh(taxon)

        # Create period rule.
        period_rule = PeriodRule(
            org_group_id=org_group.id,
            taxon_id=taxon.id,
            start_date=date(2020, 1, 1),
            end_date=date(2020, 12, 31)
        )
        db.add(period_rule)
        db.commit()
        db.refresh(period_rule)

        # Request period rules for org_group.
        response = client.get(
            f'/rules/period/org_group/{org_group.id}')
        assert response.status_code == 200
        result = response.json()
        assert result == [{
            'tvk': 'NBNSYS0000008319',
            'taxon': 'Adalia bipunctata',
            'start_date': '2020-01-01',
            'end_date': '2020-12-31'
        }]

        # Request period rules for tvk.
        response = client.get(f'/rules/period/tvk/{taxon.tvk}')
        assert response.status_code == 200
        result = response.json()
        assert result == [{
            'organisation': 'organisation1',
            'group': 'group1',
            'start_date': '2020-01-01',
            'end_date': '2020-12-31'
        }]
