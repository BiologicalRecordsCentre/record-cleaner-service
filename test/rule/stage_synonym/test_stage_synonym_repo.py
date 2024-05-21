import os

from sqlmodel import Session

from app.rule.stage_synonym.stage_repo import StageSynonymRepo
from app.sqlmodels import OrgGroup


class TestStageSynonymRepo:
    """Tests of the repo class."""

    def test_stage_synonym_repo(self, session: Session):
        # Create an org_group.
        org_group = OrgGroup(organisation='organisation1', group='group1')
        session.add(org_group)
        session.commit()
        session.refresh(org_group)

        # Locate the directory of test data.
        thisdir = os.path.abspath(os.path.dirname(__file__))
        dir = os.path.join(thisdir, 'testdata')

        # Load a file.
        repo = StageSynonymRepo(session)
        repo.load_file(dir, org_group.id, 'abc123', 'stage_synonyms_3.csv')
        result = repo.list(org_group.id)

        # Check the results.
        assert len(result) == 3
        assert result[0]['stage'] == 'mature'
        assert result[0]['synonyms'] == 'Adult, Grown up, Big boy'
        assert result[1]['stage'] == 'immature'
        assert result[1]['synonyms'] == 'Child, Kid, Teenager'
        assert result[1]['stage'] == 'infant'
        assert result[1]['synonyms'] == 'Baby, Parasite'

        # Load a shorter file.
        repo.load_file(dir, org_group.id, 'xyz321', 'stage_synonyms_1.csv')
        result = repo.list(org_group.id)

        # Check the results.
        assert len(result) == 1
        assert result[0]['stage'] == 'mature'
        assert result[0]['synonyms'] == 'Adult, Pensioner, Crumbly'

        # Load a longer file.
        repo.load_file(dir, org_group.id, 'pqr987', 'stage_synonyms_2.csv')
        result = repo.list(org_group.id)

        # Check the results.
        assert len(result) == 2
        assert result[0]['stage'] == 'mature'
        assert result[0]['synonyms'] == 'Woman, Female'
        assert result[1]['stage'] == 'immature'
        assert result[1]['synonyms'] == 'Man, Male'
