import datetime
import os
from pathlib import Path

import pytest
from sqlmodel import Session

from app.rule.period.period_repo import PeriodRuleRepo
from app.settings_env import EnvSettings
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

    def test_load_file(self, db: Session, env: EnvSettings, testdatadir: str):
        # Create org_groups.
        org_group1 = OrgGroup(organisation='organisation1', group='group1')
        org_group2 = OrgGroup(organisation='organisation2', group='group2')
        db.add(org_group1)
        db.add(org_group2)
        db.commit()
        db.refresh(org_group1)
        db.refresh(org_group2)

        # Load a file.
        repo = PeriodRuleRepo(db, env)
        errors = repo.load_file(
            testdatadir, org_group1.id, 'abc123', 'period_2.csv'
        )
        assert (errors == [])

        # Check the results by org_group.
        result = repo.list_by_org_group(org_group1.id)
        assert result[0]['organism_key'] == 'NBNORG0000010513'
        assert result[0]['taxon'] == 'Adalia bipunctata'
        assert result[0]['start_date'] == '2001-01-01'
        assert result[0]['end_date'] == '2021-12-31'
        assert result[1]['organism_key'] == 'NBNORG0000010514'
        assert result[1]['taxon'] == 'Adalia decempunctata'
        assert result[1]['start_date'] == '2002-02-02'
        assert result[1]['end_date'] == '2022-12-31'

        # Load a shorter file.
        errors = repo.load_file(
            testdatadir, org_group1.id, 'xyz321', 'period_1.csv')
        assert (errors == [])

        # Check the results by org_group.
        result = repo.list_by_org_group(org_group1.id)
        assert result[0]['organism_key'] == 'NBNORG0000010513'
        assert result[0]['taxon'] == 'Adalia bipunctata'
        assert result[0]['start_date'] == '1901-01-01'
        assert result[0]['end_date'] == '2021-12-31'

        # Load a period rule of the same taxon to another org_group.
        errors = repo.load_file(
            testdatadir, org_group2.id, 'pqr987', 'period_1_2.csv')
        assert (errors == [])

        # Check the results by organism_key.
        result = repo.list_by_organism_key('NBNORG0000010513')
        assert result[0]['organisation'] == org_group1.organisation
        assert result[0]['group'] == org_group1.group
        assert result[0]['start_date'] == '1901-01-01'
        assert result[0]['end_date'] == '2021-12-31'
        assert result[1]['organisation'] == org_group2.organisation
        assert result[1]['group'] == org_group2.group
        assert result[1]['start_date'] == '1965-11-01'
        assert result[1]['end_date'] == '2000-11-11'

    def test_load_file_date_errors(
            self, db: Session, env: EnvSettings, testdatadir: str
    ):
        # Create org_groups.
        org_group1 = OrgGroup(organisation='organisation1', group='group1')
        db.add(org_group1)
        db.commit()

        # Load a file.
        repo = PeriodRuleRepo(db, env)
        errors = repo.load_file(
            testdatadir, org_group1.id, 'abc123', 'period_errs.csv'
        )
        assert (len(errors) == 10)
        assert errors[0] == (
            "Invalid start date for NBNORG0000010513: day is out of range for "
            "month")
        assert errors[1] == (
            "Invalid start date for NBNORG0000010518: month must be in 1..12")
        assert errors[2] == (
            "Invalid end date for NBNORG0000010513: day is out of range for "
            "month")
        assert errors[3] == (
            "Invalid end date for NBNORG0000010518: month must be in 1..12")
        assert errors[4] == "Incomplete start date for NBNORG0000010513."
        assert errors[5] == "Incomplete start date for NBNORG0000010518."
        assert errors[6] == "Incomplete start date for NBNORG0000010517."
        assert errors[7] == "Incomplete end date for NBNORG0000010513."
        assert errors[8] == "Incomplete end date for NBNORG0000010518."
        assert errors[9] == "Incomplete end date for NBNORG0000010517."

    def test_file_updated(self, db: Session, env: EnvSettings, testdatadir: str):
        repo = PeriodRuleRepo(db, env)
        time_before = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        Path(f'{testdatadir}/period_1.csv').touch()
        time_modified = repo.file_updated(testdatadir, 'period_1.csv')

        assert time_modified >= time_before

    def test_run(self, db: Session, env: EnvSettings):
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
            preferred=True,
            organism_key='NBNORG0000010513',
        )
        db.add(taxon1)
        db.commit()

        # Create period rule for org_group1 and taxon1.
        rule1 = PeriodRule(
            org_group_id=org_group1.id,
            organism_key=taxon1.organism_key,
            taxon=taxon1.name,
            start_date='1970-01-01',
            end_date='1979-12-31'
        )
        # Create period rule for org_group2 and taxon1.
        rule2 = PeriodRule(
            org_group_id=org_group2.id,
            organism_key=taxon1.organism_key,
            taxon=taxon1.name,
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
            organism_key=taxon1.organism_key
        )

        repo = PeriodRuleRepo(db, env)

        # Test the record against all rules.
        ok, messages = repo.run(record)
        # It falls within both rules.
        assert ok is True
        assert len(messages) == 0

        # Change the date to fall before rule 2.
        record.date = '1/6/1970'
        ok, messages = repo.run(record)
        assert ok is False
        assert len(messages) == 1
        assert messages[0] == (
            "organisation2:group2:period: " +
            "Record is before introduction date of 1971-01-01"
        )

        # Change the date to fall before rule 1 and 2.
        record.date = '1/6/1969'
        ok, messages = repo.run(record)
        assert ok is False
        assert len(messages) == 2
        assert messages[0] == (
            "organisation1:group1:period: " +
            "Record is before introduction date of 1970-01-01"
        )
        assert messages[1] == (
            "organisation2:group2:period: " +
            "Record is before introduction date of 1971-01-01"
        )

        # Change the date to fall after rule 2.
        record.date = '1/6/1979'
        ok, messages = repo.run(record)
        assert ok is False
        assert len(messages) == 1
        assert messages[0] == (
            "organisation2:group2:period: " +
            "Record follows extinction date of 1978-12-31"
        )

        # Change the date to fall after rule 1 and 2.
        record.date = '1/6/1980'
        ok, messages = repo.run(record)
        assert ok is False
        assert len(messages) == 2
        assert messages[0] == (
            "organisation1:group1:period: " +
            "Record follows extinction date of 1979-12-31"
        )
        assert messages[1] == (
            "organisation2:group2:period: " +
            "Record follows extinction date of 1978-12-31"
        )
