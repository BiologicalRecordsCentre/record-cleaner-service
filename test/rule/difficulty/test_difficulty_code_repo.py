import os

from sqlmodel import Session

from app.rule.difficulty.difficulty_code_repo import DifficultyCodeRepo
from app.settings_env import EnvSettings
from app.sqlmodels import OrgGroup


class TestDifficultyCodeRepo:
    """Tests of the repo class."""

    def test_difficulty_code_repo(self, db: Session, env: EnvSettings):
        # Create an org_group.
        org_group = OrgGroup(organisation='organisation1', group='group1')
        db.add(org_group)
        db.commit()
        db.refresh(org_group)

        # Locate the directory of test data.
        thisdir = os.path.abspath(os.path.dirname(__file__))
        dir = os.path.join(thisdir, 'testdata')

        # Load a file.
        repo = DifficultyCodeRepo(db, env)
        repo.load_file(dir, org_group.id, 'abc123', 'difficulty_codes_3.csv')
        result = repo.list(org_group.id)

        # Check the results.
        assert (result == [
            {'difficulty': 1, 'text': 'Easy'},
            {'difficulty': 3, 'text': 'Difficult'},
            {'difficulty': 5, 'text': 'Impossible'}
        ])

        # Load a shorter file.
        repo.load_file(dir, org_group.id, 'xyz321', 'difficulty_codes_1.csv')
        result = repo.list(org_group.id)

        # Check the results.
        assert (result == [
            {'difficulty': 1, 'text': 'Easypeasy'}
        ])

        # Load a longer file.
        repo.load_file(dir, org_group.id, 'pqr987', 'difficulty_codes_2.csv')
        result = repo.list(org_group.id)

        # Check the results.
        assert (result == [
            {'difficulty': 1, 'text': 'Easy'},
            {'difficulty': 2, 'text': 'Difficult'},
        ])
