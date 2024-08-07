import os

from sqlmodel import Session

from app.rule.tenkm.tenkm_repo import TenkmRuleRepo
from app.sqlmodels import OrgGroup, Taxon, TenkmRule
from app.utility.sref import Sref, SrefSystem
from app.utility.sref.sref_factory import SrefFactory
from app.verify.verify_models import Verified


class TestTenkmRuleRepo:
    """Tests of the repo class."""

    def test_load_file(self, session: Session):
        # Create org_groups.
        org_group1 = OrgGroup(organisation='organisation1', group='group1')
        org_group2 = OrgGroup(organisation='organisation2', group='group2')
        session.add(org_group1)
        session.add(org_group2)
        session.commit()
        session.refresh(org_group1)
        session.refresh(org_group2)

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
        taxon3 = Taxon(
            name='Coccinella quinquepunctata',
            tvk='NBNSYS0000008323',
            preferred_name='Coccinella quinquepunctata',
            preferred_tvk='NBNSYS0000008323'
        )
        session.add(taxon1)
        session.add(taxon2)
        session.add(taxon3)
        session.commit()
        session.refresh(taxon1)
        session.refresh(taxon2)
        session.refresh(taxon3)

        # Locate the directory of test data.
        thisdir = os.path.abspath(os.path.dirname(__file__))
        dir = os.path.join(thisdir, 'testdata')

        # Load a file. 3 taxa in 3 coord systems.
        repo = TenkmRuleRepo(session)
        errors = repo.load_file(
            dir, org_group1.id, 'abc123', 'tenkm_3_species.csv')
        assert (errors == [])

        # Check the results by org_group.
        result = repo.list_by_org_group(org_group1.id)
        assert len(result) == 3
        assert result[0]['tvk'] == taxon1.tvk
        assert result[0]['taxon'] == taxon1.name
        assert result[0]['km100'] == 'NH'
        assert result[0]['km10'] == '01'
        assert result[0]['coord_system'] == 'OSGB'
        assert result[1]['tvk'] == taxon2.tvk
        assert result[1]['taxon'] == taxon2.name
        assert result[1]['km100'] == 'J'
        assert result[1]['km10'] == '11 12'
        assert result[1]['coord_system'] == 'OSNI'
        assert result[2]['tvk'] == taxon3.tvk
        assert result[2]['taxon'] == taxon3.name
        assert result[2]['km100'] == 'WV'
        assert result[2]['km10'] == '64 65 66'
        assert result[2]['coord_system'] == 'CI'

        # Load a shorter file. 1 taxon in 2 km100.
        errors = repo.load_file(
            dir, org_group1.id, 'xyz321', 'tenkm_1_species.csv')
        assert (errors == [])

        # Check the results by org_group.
        result = repo.list_by_org_group(org_group1.id)
        assert len(result) == 2
        assert result[0]['tvk'] == taxon1.tvk
        assert result[0]['taxon'] == taxon1.name
        assert result[0]['km100'] == 'SP'
        assert result[0]['km10'] == '99'
        assert result[0]['coord_system'] == 'OSGB'
        assert result[1]['tvk'] == taxon1.tvk
        assert result[1]['taxon'] == taxon1.name
        assert result[1]['km100'] == 'TL'
        assert result[1]['km10'] == '00'
        assert result[1]['coord_system'] == 'OSGB'

        # Load the shorter file to another org_group.
        errors = repo.load_file(
            dir, org_group2.id, 'pqr987', 'tenkm_1_species.csv')
        assert (errors == [])

        # Check the results by tvk.
        result = repo.list_by_tvk(taxon1.tvk)
        assert result[0]['organisation'] == org_group1.organisation
        assert result[0]['group'] == org_group1.group
        assert result[0]['km100'] == 'SP'
        assert result[0]['km10'] == '99'
        assert result[0]['coord_system'] == 'OSGB'
        assert result[1]['organisation'] == org_group1.organisation
        assert result[1]['group'] == org_group1.group
        assert result[1]['km100'] == 'TL'
        assert result[1]['km10'] == '00'
        assert result[1]['coord_system'] == 'OSGB'
        assert result[2]['organisation'] == org_group2.organisation
        assert result[2]['group'] == org_group2.group
        assert result[2]['km100'] == 'SP'
        assert result[2]['km10'] == '99'
        assert result[2]['coord_system'] == 'OSGB'
        assert result[3]['organisation'] == org_group2.organisation
        assert result[3]['group'] == org_group2.group
        assert result[3]['km100'] == 'TL'
        assert result[3]['km10'] == '00'
        assert result[3]['coord_system'] == 'OSGB'

    def test_run(self, session: Session):
        # Create org_groups.
        org_group1 = OrgGroup(organisation='organisation1', group='group1')
        org_group2 = OrgGroup(organisation='organisation2', group='group2')
        org_group3 = OrgGroup(organisation='organisation3', group='group3')
        session.add(org_group1)
        session.add(org_group2)
        session.add(org_group3)
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

        # Create tenkm rule for org_group1 and taxon1.
        rule1 = TenkmRule(
            org_group_id=org_group1.id,
            taxon_id=taxon1.id,
            km100='TL',
            km10='13',
            coord_system='OSGB'
        )
        # Create period rule for org_group2 and taxon1.
        rule2 = TenkmRule(
            org_group_id=org_group2.id,
            taxon_id=taxon1.id,
            km100='TL',
            km10='57',
            coord_system='OSGB'
        )
        # Create period rule for org_group2 and taxon1.
        rule3 = TenkmRule(
            org_group_id=org_group3.id,
            taxon_id=taxon1.id,
            km100='TM',
            km10='99',
            coord_system='OSGB'
        )
        session.add(rule1)
        session.add(rule2)
        session.add(rule3)
        session.commit()

        # Create record of taxon1 to test.
        record = Verified(
            id=1,
            date='1/6/1975',
            sref=SrefFactory(
                Sref(gridref='TL1234', srid=SrefSystem.GB_GRID)
            ).value,
            tvk=taxon1.tvk
        )

        repo = TenkmRuleRepo(session)

        # Test the record against org_group1 rules.
        failures = repo.run(record, org_group1.id)
        # It should pass.
        assert len(failures) == 0

        # Test the record against org_group2 rules.
        failures = repo.run(record, org_group2.id)
        # It should fail as wrong km10.
        assert len(failures) == 1
        assert failures[0] == (
            "organisation2:group2:tenkm: Record is outside known area."
        )

        # Test the record against org_group3 rules.
        failures = repo.run(record, org_group3.id)
        # It should fail as wrong km100.
        assert len(failures) == 1
        assert failures[0] == (
            "organisation3:group3:tenkm: Record is outside known area."
        )

        # Change the record to taxon2 for which there are no rules.
        record.tvk = taxon2.tvk

        # Test the record against org_group1 rules.
        failures = repo.run(record, org_group1.id)
        # It should fail as no rule.
        assert len(failures) == 1
        assert failures[0] == (
            "organisation1:group1:tenkm: There is no rule for this taxon."
        )

        # Test the record against all rules.
        failures = repo.run(record)
        # It should fail as no rule.
        assert len(failures) == 1
        assert failures[0] == (
            "*:*:tenkm: There is no rule for this taxon."
        )
