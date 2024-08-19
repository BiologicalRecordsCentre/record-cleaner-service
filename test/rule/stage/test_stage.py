from fastapi.testclient import TestClient
from sqlmodel import Session

from app.sqlmodels import OrgGroup, Stage, StageSynonym


class TestStage:
    """Tests of the public API.

    Fixtures for database and authentication come from ../conftest.py"""

    def test_stage(self, client: TestClient, session: Session):
        # Create org_group.
        org_group = OrgGroup(organisation='organisation1', group='group1')
        session.add(org_group)
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

        # Create stage-synonyms.
        synonym1 = StageSynonym(
            stage_id=stage.id,
            synonym='adult'
        )
        synonym2 = StageSynonym(
            stage_id=stage.id,
            synonym='oldie'
        )
        session.add(synonym1)
        session.add(synonym2)
        session.commit()

        # Request stages for org_group.
        response = client.get(f'/rules/stage-synonyms/{org_group.id}')
        assert response.status_code == 200
        result = response.json()
        assert len(result) == 1
        assert result[0]['stage'] == 'mature'
        assert result[0]['synonyms'] == 'adult,oldie'
