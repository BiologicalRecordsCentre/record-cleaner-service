import os

from sqlmodel import Session

from app.rules.additional.additional_code_repo import AdditionalCodeRepo
from app.sqlmodels import OrgGroup


class TestAdditionalCodeRepo:
    """Tests of the repo class."""

    def test_additional_code_repo(self, session: Session):
        # Create an org_group.
        org_group = OrgGroup(organisation='organisation1', group='group1')
        session.add(org_group)
        session.commit()
        session.refresh(org_group)

        # Locate the directory of test data.
        thisdir = os.path.abspath(os.path.dirname(__file__))
        dir = os.path.join(thisdir, 'testdata')

        # Load a file.
        repo = AdditionalCodeRepo(session)
        repo.load_file(dir, org_group.id, 'abc123', 'additional_codes_3.csv')
        result = repo.list(org_group.id)

        # Check the results.
        assert (result == [
            {'code': 1, 'text': 'Rare'},
            {'code': 3, 'text': 'Very rare'},
            {'code': 5, 'text': 'Unknown'}
        ])
        assert len(result) == 3
        assert result[0]['code'] == 1
        assert result[0]['text'] == 'Rare'
        assert result[1]['code'] == 3
        assert result[1]['text'] == 'Very rare'
        assert result[2]['code'] == 5
        assert result[2]['text'] == 'Unknown'

        # Load a shorter file.
        repo.load_file(dir, org_group.id, 'xyz321', 'additional_codes_1.csv')
        result = repo.list(org_group.id)

        # Check the results.
        assert len(result) == 1
        assert result[0]['code'] == 1
        assert result[0]['text'] == 'Unknown'

        # Load a longer file.
        repo.load_file(dir, org_group.id, 'pqr987', 'additional_codes_2.csv')
        result = repo.list(org_group.id)

        # Check the results.
        assert len(result) == 2
        assert result[0]['code'] == 1
        assert result[0]['text'] == 'Rare'
        assert result[1]['code'] == 2
        assert result[1]['text'] == 'Very rare'
