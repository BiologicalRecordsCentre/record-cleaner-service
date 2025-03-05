import os

import pytest
from datetime import date, timedelta
from sqlmodel import Session

from app.rule.phenology.phenology_repo import PhenologyRuleRepo
from app.settings_env import EnvSettings
from app.sqlmodels import OrgGroup, Taxon, Stage, StageSynonym, PhenologyRule
from app.utility.sref import Sref, SrefSystem
from app.verify.verify_models import Verified


class TestPhenologyRuleRepo:
    """Tests of the repo class."""

    @pytest.fixture(name='testdatadir', autouse=True)
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

        db.add(stage1)
        db.add(stage2)
        db.add(stage3)
        db.commit()

        # Load a file.
        repo = PhenologyRuleRepo(db, env)
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

    def test_load_file_wildcard_stage(
            self, db: Session, env: EnvSettings, testdatadir: str):
        # Create org_groups.
        org_group1 = OrgGroup(organisation='organisation1', group='group1')
        db.add(org_group1)
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

        # Load a file.
        repo = PhenologyRuleRepo(db, env)
        errors = repo.load_file(
            testdatadir, org_group1.id, 'abc123', 'periodwithinyear_1_3.csv'
        )
        assert (errors == [])

        # Check the results by org_group.
        result = repo.list_by_org_group(org_group1.id)
        assert len(result) == 1
        assert result[0]['tvk'] == taxon1.tvk
        assert result[0]['taxon'] == taxon1.name
        assert result[0]['start_date'] == '2/6'
        assert result[0]['end_date'] == '29/11'
        assert result[0]['stage'] == '*'

    def test_run(self, db: Session, env: EnvSettings):
        # Create org_groups.
        org_group1 = OrgGroup(organisation='organisation1', group='group1')
        org_group2 = OrgGroup(organisation='organisation2', group='group2')
        org_group3 = OrgGroup(organisation='organisation3', group='group3')
        db.add(org_group1)
        db.add(org_group2)
        db.add(org_group3)
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
        stage4 = Stage(
            org_group_id=org_group3.id,
            stage='*',
            sort_order=1
        )
        db.add(stage1)
        db.add(stage2)
        db.add(stage3)
        db.add(stage4)
        db.commit()

        # Create stage-synonyms.
        synonym1 = StageSynonym(
            stage_id=stage1.id,
            synonym='adult'
        )
        synonym2 = StageSynonym(
            stage_id=stage2.id,
            synonym='larval'
        )
        db.add(synonym1)
        db.add(synonym2)
        db.commit()

        # Create phenology rule for org_group1 and mature taxon1.
        rule1 = PhenologyRule(
            org_group_id=org_group1.id,
            taxon_id=taxon1.id,
            stage_id=stage1.id,
            start_day=8,
            start_month=6,
            end_day=6,
            end_month=10
        )
        # Create phenology rule for org_group1 and larval taxon1.
        rule2 = PhenologyRule(
            org_group_id=org_group1.id,
            taxon_id=taxon1.id,
            stage_id=stage2.id,
            start_day=31,
            start_month=3,
            end_day=30,
            end_month=6
        )
        # Create phenology rule for org_group2 and mature taxon1.
        rule3 = PhenologyRule(
            org_group_id=org_group2.id,
            taxon_id=taxon1.id,
            stage_id=stage3.id,
            start_day=11,
            start_month=7,
            end_day=12,
            end_month=9
        )
        # Create phenology rule for org_group3 and taxon1 at any stage.
        rule4 = PhenologyRule(
            org_group_id=org_group3.id,
            taxon_id=taxon1.id,
            stage_id=stage4.id,
            start_day=1,
            start_month=2,
            end_day=30,
            end_month=11
        )
        db.add(rule1)
        db.add(rule2)
        db.add(rule3)
        db.add(rule4)
        db.commit()

        # Create record of taxon1 to test.
        record = Verified(
            id=1,
            date='1/8/1975',
            sref=Sref(gridref='TL123456', srid=SrefSystem.GB_GRID),
            preferred_tvk=taxon1.preferred_tvk,
            stage='adult'
        )

        repo = PhenologyRuleRepo(db, env)

        # Test the record against rules for org_group1.
        ok, messages = repo.run(record, org_group1.id)
        # It should pass.
        assert ok is True
        assert len(messages) == 0

        # Test the record against rules for all org_groups.
        ok, messages = repo.run(record)
        # It should pass.
        assert ok is True
        assert len(messages) == 0

        # Remove the stage.
        record.stage = None
        # Test the record against rules for all org_groups.
        ok, messages = repo.run(record)
        # It should pass as defaults to mature.
        assert ok is True
        assert len(messages) == 0

        # Change to larval stage.
        record.stage = 'larval'
        # Test the record against rules for org_group1.
        ok, messages = repo.run(record, org_group1.id)
        # It should fail as date out of range.
        assert ok is False
        assert len(messages) == 1
        assert messages[0] == (
            "organisation1:group1:phenology:larval:"
            "Date is outside the expected period of 31/3 - 30/6."
        )

        # Test the record against wildcard rule of org_group3.
        ok, messages = repo.run(record, org_group3.id)
        # It should pass.
        assert ok is True
        assert len(messages) == 0

        # Change to taxon2 with no rules.
        record.preferred_tvk = taxon2.preferred_tvk
        # Test the record against rules for all org_groups.
        ok, messages = repo.run(record)
        # It should baulk
        assert ok is None
        assert len(messages) == 0

        # Test the record against rules for org_group1.
        ok, messages = repo.run(record, org_group1.id)
        # It should baulk.
        assert ok is None
        assert len(messages) == 0

    def test_test(self, db: Session, env: EnvSettings):

        record = Verified(
            id=1,
            date='1/8/1975',
            sref=Sref(gridref='TL123456', srid=SrefSystem.GB_GRID),
            tvk='NBNSYS0000008319',
            stage='adult'
        )

        # Create a summer rule.
        rule = PhenologyRule(
            org_group_id=1,
            taxon_id=1,
            stage_id=1,
            start_day=8,
            start_month=6,
            end_day=6,
            end_month=10
        )

        repo = PhenologyRuleRepo(db, env)

        # Single date within rule
        assert repo.test(record, rule) is None
        # Single date on rule start
        record.date = '8/6/1975'
        assert repo.test(record, rule) is None
        # Single date on rule end
        record.date = '6/10/1975'
        assert repo.test(record, rule) is None
        # Date range within rule.
        record.date = '1/8/1975 - 10/8/1975'
        assert repo.test(record, rule) is None
        # Date range overlapping start of rule.
        record.date = '1/6/1975 - 1/8/1975'
        assert repo.test(record, rule) is None
        # Date range overlapping end of rule.
        record.date = '1/8/1975 - 1/11/1975'
        assert repo.test(record, rule) is None
        # Date range overlapping entire rule.
        record.date = '1/6/1975 - 1/11/1975'
        assert repo.test(record, rule) is None
        # Date range in excess of a year
        record.date = '1/10/1975 - 1/11/1976'
        assert repo.test(record, rule) is None

        # Single date just before rule
        record.date = '7/6/1975'
        failure = repo.test(record, rule)
        assert failure == (
            "Date is outside the expected period of 8/6 - 6/10."
        )
        # Single date just after rule
        record.date = '7/10/1975'
        failure = repo.test(record, rule)
        assert failure == (
            "Date is outside the expected period of 8/6 - 6/10."
        )
        # Date range outside rule
        record.date = '1/11/1975 - 1/2/1976'
        failure = repo.test(record, rule)
        assert failure == (
            "Date is outside the expected period of 8/6 - 6/10."
        )

        # Change to a winter rule.
        rule.start_month = 10
        rule.end_month = 3

        # Single date within rule before new year.
        record.date = '1/12/1975'
        assert repo.test(record, rule) is None
        # Single date within rule after new year.
        record.date = '1/2/1975'
        assert repo.test(record, rule) is None
        # Single date on rule start
        record.date = '8/10/1975'
        assert repo.test(record, rule) is None
        # Single date on rule end
        record.date = '6/3/1975'
        assert repo.test(record, rule) is None
        # Date range within rule.
        record.date = '1/12/1975 - 1/2/1976'
        assert repo.test(record, rule) is None
        # Date range overlapping start of rule.
        record.date = '1/10/1975 - 1/11/1975'
        assert repo.test(record, rule) is None
        # Date range overlapping end of rule.
        record.date = '1/2/1975 - 1/4/1975'
        assert repo.test(record, rule) is None
        # Date range overlapping entire rule.
        record.date = '1/10/1975 - 1/4/1976'
        assert repo.test(record, rule) is None
        # Date range in excess of a year
        record.date = '1/6/1975 - 1/7/1976'
        assert repo.test(record, rule) is None

        # Single date just before rule
        record.date = '7/10/1975'
        failure = repo.test(record, rule)
        assert failure == (
            "Date is outside the expected period of 8/10 - 6/3."
        )
        # Single date just after rule
        record.date = '7/3/1975'
        failure = repo.test(record, rule)
        assert failure == (
            "Date is outside the expected period of 8/10 - 6/3."
        )
        # Date range outside rule
        record.date = '1/5/1975 - 1/8/1975'
        failure = repo.test(record, rule)
        assert failure == (
            "Date is outside the expected period of 8/10 - 6/3."
        )

    def test_test_tolerant(self, db: Session, env_tolerant: EnvSettings):

        record = Verified(
            id=1,
            date='1/8/1975',
            sref=Sref(gridref='TL123456', srid=SrefSystem.GB_GRID),
            tvk='NBNSYS0000008319',
            stage='adult'
        )

        # Create a summer rule.
        rule = PhenologyRule(
            org_group_id=1,
            taxon_id=1,
            stage_id=1,
            start_day=8,
            start_month=6,
            end_day=6,
            end_month=10
        )

        repo = PhenologyRuleRepo(db, env_tolerant)
        tolerance = timedelta(days=int(env_tolerant.phenology_tolerance))
        oneday = timedelta(days=1)

        # Single date just before rule
        record.date = (date(1975, 6, 8) - tolerance).isoformat()
        failure = repo.test(record, rule)
        assert failure == (
            "Date is CLOSE TO the expected period of 8/6 - 6/10."
        )
        # Single date significantly before rule
        record.date = (date(1975, 6, 8) - tolerance - oneday).isoformat()
        failure = repo.test(record, rule)
        assert failure == (
            "Date is FAR FROM the expected period of 8/6 - 6/10."
        )
        # Single date just after rule
        record.date = (date(1975, 10, 6) + tolerance).isoformat()
        failure = repo.test(record, rule)
        assert failure == (
            "Date is CLOSE TO the expected period of 8/6 - 6/10."
        )
        # Single date significantly after rule
        record.date = (date(1975, 10, 6) + tolerance + oneday).isoformat()
        failure = repo.test(record, rule)
        assert failure == (
            "Date is FAR FROM the expected period of 8/6 - 6/10."
        )
        # Date range just outside rule
        record.date = '7/10/1975 - 7/6/1976'
        failure = repo.test(record, rule)
        assert failure == (
            "Date is CLOSE TO the expected period of 8/6 - 6/10."
        )
        # Date range significantly outside rule
        record.date = '1/11/1975 - 1/2/1976'
        failure = repo.test(record, rule)
        assert failure == (
            "Date is FAR FROM the expected period of 8/6 - 6/10."
        )

        # Change to a winter rule.
        rule.start_month = 10
        rule.end_month = 3

        # Single date just before rule
        record.date = (date(1975, 10, 8) - tolerance).isoformat()
        failure = repo.test(record, rule)
        assert failure == (
            "Date is CLOSE TO the expected period of 8/10 - 6/3."
        )
        # Single date significantly before rule
        record.date = (date(1975, 10, 8) - tolerance - oneday).isoformat()
        failure = repo.test(record, rule)
        assert failure == (
            "Date is FAR FROM the expected period of 8/10 - 6/3."
        )
        # Single date just after rule
        record.date = (date(1975, 3, 6) + tolerance).isoformat()
        failure = repo.test(record, rule)
        assert failure == (
            "Date is CLOSE TO the expected period of 8/10 - 6/3."
        )
        # Single date significantly after rule
        record.date = (date(1975, 3, 6) + tolerance + oneday).isoformat()
        failure = repo.test(record, rule)
        assert failure == (
            "Date is FAR FROM the expected period of 8/10 - 6/3."
        )
        # Date range just outside rule
        record.date = '7/3/1975 - 7/10/1975'
        failure = repo.test(record, rule)
        assert failure == (
            "Date is CLOSE TO the expected period of 8/10 - 6/3."
        )
        # Date range significantly outside rule
        record.date = '1/5/1975 - 1/8/1975'
        failure = repo.test(record, rule)
        assert failure == (
            "Date is FAR FROM the expected period of 8/10 - 6/3."
        )
