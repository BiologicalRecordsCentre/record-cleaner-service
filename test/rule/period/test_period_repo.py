import datetime
import os
from pathlib import Path

import pytest
from sqlmodel import Session

from app.rule.period.period_repo import PeriodRuleRepo
from app.sqlmodels import OrgGroup, Taxon, PeriodRule
from app.utility.sref import Sref, SrefSystem
from app.verify.verify_models import Verified


class TestPeriodRuleRepo:
    """Tests of the repo class."""

    @pytest.fixture(name='testdatadir')
    def testdata_fixture(self):
        # Locate the directory of test data.
        thisdir = os.path.abspath(os.path.dirname(__file__))
        return os.path.join(thisdir, 'testdata')

    def test_load_file(self, db: Session, testdatadir: str):
        # Create org_groups.
        org_group1 = OrgGroup(organisation='organisation1', group='group1')
        org_group2 = OrgGroup(organisation='organisation2', group='group2')
        db.add(org_group1)
        db.add(org_group2)
        db.commit()
        db.refresh(org_group1)
        db.refresh(org_group2)

        # Create taxa.
        taxon1 = Taxon(
            name='Adalia bipunctata',
            preferred_name='Adalia bipunctata',
            search_name='adaliabipunctata',
            tvk='NBNSYS0000008319',
            preferred_tvk='NBNSYS0000008319',
            preferred=True
        )
        taxon2 = Taxon(
            name='Adalia decempunctata',
            preferred_name='Adalia decempunctata',
            search_name='adaliadecempunctata',
            tvk='NBNSYS0000008320',
            preferred_tvk='NBNSYS0000008320',
            preferred=True
        )
        db.add(taxon1)
        db.add(taxon2)
        db.commit()
        db.refresh(taxon1)
        db.refresh(taxon2)

        # Load a file.
        repo = PeriodRuleRepo(db)
        errors = repo.load_file(
            testdatadir, org_group1.id, 'abc123', 'period_2.csv'
        )
        assert (errors == [])

        # Check the results by org_group.
        result = repo.list_by_org_group(org_group1.id)
        assert result[0]['tvk'] == taxon1.tvk
        assert result[0]['taxon'] == taxon1.name
        assert result[0]['start_date'] == '2001-01-01'
        assert result[0]['end_date'] == '2021-12-31'
        assert result[1]['tvk'] == taxon2.tvk
        assert result[1]['taxon'] == taxon2.name
        assert result[1]['start_date'] == '2002-02-02'
        assert result[1]['end_date'] == '2022-12-31'

        # Load a shorter file.
        errors = repo.load_file(
            testdatadir, org_group1.id, 'xyz321', 'period_1.csv')
        assert (errors == [])

        # Check the results by org_group.
        result = repo.list_by_org_group(org_group1.id)
        assert result[0]['tvk'] == taxon1.tvk
        assert result[0]['taxon'] == taxon1.name
        assert result[0]['start_date'] == '1901-01-01'
        assert result[0]['end_date'] == '2021-12-31'

        # Load a period rule of the same taxon to another org_group.
        errors = repo.load_file(
            testdatadir, org_group2.id, 'pqr987', 'period_1_2.csv')
        assert (errors == [])

        # Check the results by tvk.
        result = repo.list_by_tvk(taxon1.tvk)
        assert result[0]['organisation'] == org_group1.organisation
        assert result[0]['group'] == org_group1.group
        assert result[0]['start_date'] == '1901-01-01'
        assert result[0]['end_date'] == '2021-12-31'
        assert result[1]['organisation'] == org_group2.organisation
        assert result[1]['group'] == org_group2.group
        assert result[1]['start_date'] == '1965-11-01'
        assert result[1]['end_date'] == '2000-11-11'

    def test_file_updated(self, db: Session, testdatadir: str):
        repo = PeriodRuleRepo(db)
        time_before = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        Path(f'{testdatadir}/period_1.csv').touch()
        time_modified = repo.file_updated(testdatadir, 'period_1.csv')

        assert time_modified >= time_before

    def test_run(self, db: Session):
        # Create org_groups.
        org_group1 = OrgGroup(organisation='organisation1', group='group1')
        org_group2 = OrgGroup(organisation='organisation2', group='group2')
        db.add(org_group1)
        db.add(org_group2)
        db.commit()

        # Create taxa.
        taxon1 = Taxon(
            name='Adalia bipunctata',
            preferred_name='Adalia bipunctata',
            search_name='adaliabipunctata',
            tvk='NBNSYS0000008319',
            preferred_tvk='NBNSYS0000008319',
            preferred=True
        )
        db.add(taxon1)
        db.commit()

        # Create period rule for org_group1 and taxon1.
        rule1 = PeriodRule(
            org_group_id=org_group1.id,
            taxon_id=taxon1.id,
            start_date='1970-01-01',
            end_date='1979-12-31'
        )
        # Create period rule for org_group2 and taxon1.
        rule2 = PeriodRule(
            org_group_id=org_group2.id,
            taxon_id=taxon1.id,
            start_date='1971-01-01',
            end_date='1978-12-31'
        )
        db.add(rule1)
        db.add(rule2)
        db.commit()

        # Create record of taxon1 to test.
        record = Verified(
            id=1,
            date='1/6/1975',
            sref=Sref(gridref='TL123456', srid=SrefSystem.GB_GRID),
            preferred_tvk=taxon1.preferred_tvk
        )

        repo = PeriodRuleRepo(db)

        # Test the record against all rules.
        failures = repo.run(record)
        # It falls within both rules.
        assert len(failures) == 0

        # Change the date to fall before rule 2.
        record.date = '1/6/1970'
        failures = repo.run(record)
        assert len(failures) == 1
        assert failures[0] == (
            "organisation2:group2:period: " +
            "Record is before introduction date of 1971-01-01"
        )

        # Change the date to fall before rule 1 and 2.
        record.date = '1/6/1969'
        failures = repo.run(record)
        assert len(failures) == 2
        assert failures[0] == (
            "organisation1:group1:period: " +
            "Record is before introduction date of 1970-01-01"
        )
        assert failures[1] == (
            "organisation2:group2:period: " +
            "Record is before introduction date of 1971-01-01"
        )

        # Change the date to fall after rule 2.
        record.date = '1/6/1979'
        failures = repo.run(record)
        assert len(failures) == 1
        assert failures[0] == (
            "organisation2:group2:period: " +
            "Record follows extinction date of 1978-12-31"
        )

        # Change the date to fall after rule 1 and 2.
        record.date = '1/6/1980'
        failures = repo.run(record)
        assert len(failures) == 2
        assert failures[0] == (
            "organisation1:group1:period: " +
            "Record follows extinction date of 1979-12-31"
        )
        assert failures[1] == (
            "organisation2:group2:period: " +
            "Record follows extinction date of 1978-12-31"
        )
