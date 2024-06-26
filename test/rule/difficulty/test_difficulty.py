from fastapi.testclient import TestClient
from sqlmodel import Session

from app.sqlmodels import OrgGroup, Taxon, DifficultyCode, DifficultyRule


class TestDifficulty:
    """Tests of the public API.

    Fixtures for database and authentication come from ../conftest.py"""

    def test_difficulty(self, client: TestClient, session: Session):
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

        # Create difficulty code.
        difficulty_code = DifficultyCode(
            code=1,
            text='Easy',
            org_group_id=org_group.id
        )
        session.add(difficulty_code)
        session.commit()
        session.refresh(difficulty_code)

        # Create difficulty rule.
        difficulty_rule = DifficultyRule(
            org_group_id=org_group.id,
            taxon_id=taxon.id,
            difficulty_code_id=difficulty_code.id
        )
        session.add(difficulty_rule)
        session.commit()
        session.refresh(difficulty_rule)

        # Request difficulty codes for org_group.
        response = client.get(f'/rules/difficulty-codes/{org_group.id}')
        assert response.status_code == 200
        result = response.json()
        assert result == [{'difficulty': 1, 'text': 'Easy'}]

        # Request difficulty rules for org_group.
        response = client.get(
            f'/rules/difficulty/org_group/{org_group.id}')
        assert response.status_code == 200
        result = response.json()
        assert result[0]['tvk'] == 'NBNSYS0000008319'
        assert result[0]['taxon'] == 'Adalia bipunctata'
        assert result[0]['difficulty'] == 1

        # Request difficulty rules for tvk.
        response = client.get(f'/rules/difficulty/tvk/{taxon.tvk}')
        assert response.status_code == 200
        result = response.json()
        assert result[0]['organisation'] == 'organisation1'
        assert result[0]['group'] == 'group1'
        assert result[0]['difficulty'] == 1
        assert result[0]['text'] == 'Easy'
