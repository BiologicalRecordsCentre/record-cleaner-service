import os

from sqlmodel import Session

from app.rule.org_group.org_group_repo import OrgGroupRepo
from app.sqlmodels import OrgGroup


class TestOrgGroupRepo:
    """Tests of the repo class."""

    def test_org_group_repo(self, db: Session):

        # Locate the directory for test data.
        thisdir = os.path.abspath(os.path.dirname(__file__))
        dir = os.path.join(thisdir, 'testdata')

        # Create directory structure for orgs and groups.
        if not os.path.exists(os.path.join(dir, 'org1/group1')):
            os.makedirs(os.path.join(dir, 'org1/group1'))
        if not os.path.exists(os.path.join(dir, 'org1/group2')):
            os.makedirs(os.path.join(dir, 'org1/group2'))
        if not os.path.exists(os.path.join(dir, 'org2/group1')):
            os.makedirs(os.path.join(dir, 'org2/group1'))

        # Load file structure.
        repo = OrgGroupRepo(db)
        repo.load_dir_structure(dir, 'abc123')

        # Check the results.
        result = repo.list()
        assert len(result) == 3
        assert result[0].organisation == 'org1'
        assert result[0].group == 'group1'
        assert result[1].organisation == 'org1'
        assert result[1].group == 'group2'
        assert result[2].organisation == 'org2'
        assert result[2].group == 'group1'

        # Delete a directory.
        os.rmdir(os.path.join(dir, 'org1/group1'))

        # Load file structure.
        repo = OrgGroupRepo(db)
        repo.load_dir_structure(dir, 'xyz321')

        # Check the results.
        result = repo.list()
        assert len(result) == 2
        assert result[0].organisation == 'org1'
        assert result[0].group == 'group2'
        assert result[1].organisation == 'org2'
        assert result[1].group == 'group1'
