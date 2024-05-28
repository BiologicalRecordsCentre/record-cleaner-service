import datetime
import os
from pathlib import Path

import pytest
from sqlmodel import Session

from app.rule.phenology.phenology_repo import PhenologyRuleRepo
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

    def test_run(self, session: Session):
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
        session.add(taxon1)
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

        # Create stage-synonyms.
        synonym1 = StageSynonym(
            stage_id=stage1.id,
            synonym='adult'
        )
        session.add(synonym1)
        session.commit()

        # Create phenology rule for org_group1 and taxon1.
        rule1 = PhenologyRule(
            org_group_id=org_group1.id,
            taxon_id=taxon1.id,
            stage_id=stage1.id,
            start_day=8,
            start_month=6,
            end_day=6,
            end_month=10
        )
        # Create phenology rule for org_group2 and taxon1.
        rule2 = PhenologyRule(
            org_group_id=org_group2.id,
            taxon_id=taxon1.id,
            stage_id=stage3.id,
            start_day=11,
            start_month=7,
            end_day=12,
            end_month=9
        )
        session.add(rule1)
        session.add(rule2)
        session.commit()

        # Create record of taxon1 to test.
        record = Verified(
            id=1,
            date='1/8/1975',
            sref=Sref(gridref='TL123456', srid=SrefSystem.GB_GRID),
            tvk=taxon1.tvk,
            stage='adult'
        )

        repo = PhenologyRuleRepo(session)

        # Test the record against rules for org_group1.
        failures = repo.run(record, org_group1.id)
        # It should pass.
        assert len(failures) == 0

        # Test the record against rules for all org_groups.
        failures = repo.run(record)
        # It should fail as org_group2 has no stage synonym for adult.
        assert len(failures) == 1
        assert failures[0] == (
            "organisation2:group2:phenology: "
            "Could not find rule for stage 'adult'."
        )

    def test_test(self, session: Session):

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

        repo = PhenologyRuleRepo(session)

        # Single date within rule
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

        # Single date before rule
        record.date = '1/4/1975'
        failure = repo.test(record, rule)
        assert failure == (
            "phenology: Record is outside of expected period of 8/6 - 6/10."
        )
        # Single date after rule
        record.date = '1/11/1975'
        failure = repo.test(record, rule)
        assert failure == (
            "phenology: Record is outside of expected period of 8/6 - 6/10."
        )
        # Date range outside rule
        record.date = '7/10/1975 - 7/6/1976'
        failure = repo.test(record, rule)
        assert failure == (
            "phenology: Record is outside of expected period of 8/6 - 6/10."
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
        # Date range within rule.
        record.date = '1/12/1975 - 1/2/1976'
        assert repo.test(record, rule) is None
        # Date range overlapping start of rule.
        record.date = '1/10/1975 - 1/11/1975'
        assert repo.test(record, rule) is None
        # Date range overlapping end of rule.
        record.date = '1/2/1975 - 1/4/1975'
        assert repo.test(record, rule) is None

        # Single date before rule
        record.date = '1/10/1975'
        failure = repo.test(record, rule)
        assert failure == (
            "phenology: Record is outside of expected period of 8/10 - 6/3."
        )
        # Single date after rule
        record.date = '1/4/1975'
        failure = repo.test(record, rule)
        assert failure == (
            "phenology: Record is outside of expected period of 8/10 - 6/3."
        )
        # Date range outside rule
        record.date = '11/3/1975 - 5/10/1976'
        failure = repo.test(record, rule)
        assert failure == (
            "phenology: Record is outside of expected period of 8/10 - 6/3."
        )
