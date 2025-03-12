from fastapi.testclient import TestClient
from sqlmodel import Session

from app.sqlmodels import OrgGroup, Taxon, DifficultyCode, DifficultyRule


class TestDifficulty:
    """Tests of the public API.

    Fixtures for database and authentication come from ../conftest.py"""

    def test_difficulty(self, client: TestClient):
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

            # Create difficulty code.
            difficulty_code = DifficultyCode(
                code=1,
                text='Easy',
                org_group_id=org_group.id
            )
            db.add(difficulty_code)
            db.commit()
            db.refresh(difficulty_code)

            # Create difficulty rule.
            difficulty_rule = DifficultyRule(
                org_group_id=org_group.id,
                taxon_id=taxon.id,
                difficulty_code_id=difficulty_code.id
            )
            db.add(difficulty_rule)
            db.commit()
            db.refresh(difficulty_rule)

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
