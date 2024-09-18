from fastapi.testclient import TestClient
from sqlmodel import Session

from app.sqlmodels import OrgGroup, Stage, StageSynonym


class TestStage:
    """Tests of the public API.

    Fixtures for database and authentication come from ../conftest.py"""

    def test_stage(self, client: TestClient):
        # Get database connection from client.
        engine = client.app.context['engine']
        with Session(engine) as db:
            # Create org_group.
            org_group = OrgGroup(organisation='organisation1', group='group1')
            db.add(org_group)
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

            # Create stage-synonyms.
            synonym1 = StageSynonym(
                stage_id=stage.id,
                synonym='adult'
            )
            synonym2 = StageSynonym(
                stage_id=stage.id,
                synonym='oldie'
            )
            db.add(synonym1)
            db.add(synonym2)
            db.commit()

            # Request stages for org_group.
            response = client.get(f'/rules/stage-synonyms/{org_group.id}')
            assert response.status_code == 200
            result = response.json()
            assert len(result) == 1
            assert result[0]['stage'] == 'mature'
            assert result[0]['synonyms'] == 'adult,oldie'
