import datetime
import os
from pathlib import Path

import pytest
from sqlmodel import Session

from app.rule.phenology.phenology_rule_repo import PhenologyRuleRepo
from app.sqlmodels import OrgGroup, Taxon, Stage


class TestPhenologyRuleRepo:
    """Tests of the repo class."""

    @pytest.fixture(name='testdatadir', autouse=True)
    def testdata_fixture(self):
        # Locate the directory of test data.
        thisdir = os.path.abspath(os.path.dirname(__file__))
        return os.path.join(thisdir, 'testdata')

    def test_load_file(self, session: Session, testdatadir: str):
        # Create org_groups.
        org_group1 = OrgGroup(organisation='organisation1', group='group1')
        org_group2 = OrgGroup(organisation='organisation2', group='group2')
        session.add(org_group1)
        session.add(org_group2)
        session.commit()

        # Create taxa.
        taxon1 = Taxon(
            name='Adalia bipunctata',
            tvk='NBNSYS0000008319',
            preferred_name='Adalia bipunctata',
            preferred_tvk='NBNSYS0000008319'
        )
        taxon2 = Taxon(
            name='Adalia decempunctata',
            tvk='NBNSYS0000008320',
            preferred_name='Adalia decempunctata',
            preferred_tvk='NBNSYS0000008320'
        )
        session.add(taxon1)
        session.add(taxon2)
        session.commit()

        # Create stages.
        stage1 = Stage(
            org_group_id=org_group1.id,
            stage='mature',
            sort_order=1
        )
        stage2 = Stage(
            org_group_id=org_group1.id,
            stage='larval',
            sort_order=2
        )
        stage3 = Stage(
            org_group_id=org_group2.id,
            stage='mature',
            sort_order=1
        )

        session.add(stage1)
        session.add(stage2)
        session.add(stage3)
        session.commit()

        # Load a file.
        repo = PhenologyRuleRepo(session)
        errors = repo.load_file(
            testdatadir, org_group1.id, 'abc123', 'periodwithinyear_2.csv'
        )
        assert (errors == [])

        # Check the results by org_group.
        result = repo.list_by_org_group(org_group1.id)
        assert len(result) == 2
        assert result[0]['tvk'] == taxon1.tvk
        assert result[0]['taxon'] == taxon1.name
        assert result[0]['start_date'] == '1/4'
        assert result[0]['end_date'] == '31/10'
        assert result[0]['stage'] == 'mature'
        assert result[1]['tvk'] == taxon1.tvk
        assert result[1]['taxon'] == taxon1.name
        assert result[1]['start_date'] == '1/10'
        assert result[1]['end_date'] == '30/4'
        assert result[1]['stage'] == 'larval'

        # Load a shorter file.
        errors = repo.load_file(
            testdatadir, org_group1.id, 'xyz321', 'periodwithinyear_1.csv')
        assert (errors == [])

        # Check the results by org_group.
        result = repo.list_by_org_group(org_group1.id)
        assert len(result) == 1
        assert result[0]['tvk'] == taxon2.tvk
        assert result[0]['taxon'] == taxon2.name
        assert result[0]['start_date'] == '1/6'
        assert result[0]['end_date'] == '30/11'
        assert result[0]['stage'] == 'mature'

        # Load a rule of the same taxon to another org_group.
        errors = repo.load_file(
            testdatadir, org_group2.id, 'pqr987', 'periodwithinyear_1_2.csv')
        assert (errors == [])

        # Check the results by tvk.
        result = repo.list_by_tvk(taxon2.tvk)
        assert len(result) == 2
        assert result[0]['organisation'] == org_group1.organisation
        assert result[0]['group'] == org_group1.group
        assert result[0]['start_date'] == '1/6'
        assert result[0]['end_date'] == '30/11'
        assert result[0]['stage'] == 'mature'
        assert result[1]['organisation'] == org_group2.organisation
        assert result[1]['group'] == org_group2.group
        assert result[1]['start_date'] == '2/6'
        assert result[1]['end_date'] == '29/11'
        assert result[1]['stage'] == 'mature'

    def test_file_updated(self, session: Session, testdatadir: str):
        repo = PhenologyRuleRepo(session)
        time_before = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        Path(f'{testdatadir}/period_1.csv').touch()
        time_modified = repo.file_updated(testdatadir, 'period_1.csv')

        assert time_modified >= time_before
