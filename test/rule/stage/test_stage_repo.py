import os

from sqlmodel import Session

from app.rule.stage.stage_repo import StageRepo
from app.settings_env import EnvSettings
from app.sqlmodels import OrgGroup


class TestStageRepo:
    """Tests of the repo class."""

    def test_stage_repo(self, db: Session, env: EnvSettings):
        # Create an org_group.
        org_group = OrgGroup(organisation='organisation1', group='group1')
        db.add(org_group)
        db.commit()
        db.refresh(org_group)

        # Locate the directory of test data.
        thisdir = os.path.abspath(os.path.dirname(__file__))
        dir = os.path.join(thisdir, 'testdata')

        # Load a file.
        repo = StageRepo(db, env)
        repo.load_file(dir, org_group.id, 'abc123', 'stage_synonyms_3.csv')
        result = repo.list(org_group.id)

        # Check the results. (Synonyms are lower-cased and sorted.)
        assert len(result) == 3
        assert result[0]['stage'] == 'mature'
        assert result[0]['synonyms'] == 'adult,big boy,grown up'
        assert result[1]['stage'] == 'immature'
        assert result[1]['synonyms'] == 'child,kid,teenager'
        assert result[2]['stage'] == 'infant'
        assert result[2]['synonyms'] == 'baby,toddler'

        # Load a shorter file.
        repo.load_file(dir, org_group.id, 'xyz321', 'stage_synonyms_1.csv')
        result = repo.list(org_group.id)

        # Check the results.
        assert len(result) == 1
        assert result[0]['stage'] == 'mature'
        assert result[0]['synonyms'] == 'adult,crumbly,pensioner'

        # Load a longer file.
        repo.load_file(dir, org_group.id, 'pqr987', 'stage_synonyms_2.csv')
        result = repo.list(org_group.id)

        # Check the results.
        assert len(result) == 2
        assert result[0]['stage'] == 'mature'
        assert result[0]['synonyms'] == 'female,woman'
        assert result[1]['stage'] == 'immature'
        assert result[1]['synonyms'] == 'male,man'
