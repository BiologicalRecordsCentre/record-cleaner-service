import os

from sqlmodel import Session

from app.rule.tenkm.tenkm_repo import TenkmRuleRepo
from app.settings_env import EnvSettings
from app.sqlmodels import OrgGroup, Taxon, TenkmRule
from app.utility.sref import Sref, SrefSystem
from app.utility.sref.sref_factory import SrefFactory
from app.verify.verify_models import Verified


class TestTenkmRuleRepo:
    """Tests of the repo class."""

    def test_load_file(self, db: Session, env: EnvSettings):
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
        taxon3 = Taxon(
            name='Coccinella quinquepunctata',
            preferred_name='Coccinella quinquepunctata',
            search_name='coccinellacinquepunctata',
            tvk='NBNSYS0000008323',
            preferred_tvk='NBNSYS0000008323',
            preferred=True
        )
        db.add(taxon1)
        db.add(taxon2)
        db.add(taxon3)
        db.commit()
        db.refresh(taxon1)
        db.refresh(taxon2)
        db.refresh(taxon3)

        # Locate the directory of test data.
        thisdir = os.path.abspath(os.path.dirname(__file__))
        dir = os.path.join(thisdir, 'testdata')

        # Load a file. 3 taxa in 3 coord systems.
        repo = TenkmRuleRepo(db, env)
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

        # Create tenkm rule for org_group1 and taxon1.
        rule1 = TenkmRule(
            org_group_id=org_group1.id,
            taxon_id=taxon1.id,
            km100='TL',
            km10='13',
            coord_system='OSGB'
        )
        # Create tenkm rule for org_group2 and taxon1.
        rule2 = TenkmRule(
            org_group_id=org_group2.id,
            taxon_id=taxon1.id,
            km100='TL',
            km10='57',
            coord_system='OSGB'
        )
        # Create tenkm rule for org_group3 and taxon1.
        rule3 = TenkmRule(
            org_group_id=org_group3.id,
            taxon_id=taxon1.id,
            km100='TM',
            km10='99',
            coord_system='OSGB'
        )
        db.add(rule1)
        db.add(rule2)
        db.add(rule3)
        db.commit()

        # Create record of taxon1 to test.
        record = Verified(
            id=1,
            date='1/6/1975',
            sref=SrefFactory(
                Sref(gridref='TL1234', srid=SrefSystem.GB_GRID)
            ).value,
            preferred_tvk=taxon1.preferred_tvk
        )

        repo = TenkmRuleRepo(db, env)

        # Test the record against org_group1 rules.
        ok, messages = repo.run(record, org_group1.id)
        # It should pass.
        assert ok is True
        assert len(messages) == 0

        # Test the record against org_group2 rules.
        ok, messages = repo.run(record, org_group2.id)
        # It should fail as wrong km10.
        assert ok is False
        assert len(messages) == 1
        assert messages[0] == (
            "organisation2:group2:tenkm: Record is outside known area."
        )

        # Test the record against org_group3 rules.
        ok, messages = repo.run(record, org_group3.id)
        # It should fail as wrong km100.
        assert ok is False
        assert len(messages) == 1
        assert messages[0] == (
            "organisation3:group3:tenkm: Record is outside known area."
        )

        # Change the location of the record to be in 10km TL23.
        record.sref = SrefFactory(
            Sref(gridref='TL2234', srid=SrefSystem.GB_GRID)
        ).value

        # Test the record against org_group1 rules.
        ok, messages = repo.run(record, org_group1.id)
        # It should just fail as adjacent to a valid square.
        assert ok is False
        assert len(messages) == 1
        assert messages[0] == (
            "organisation1:group1:tenkm: Record is just outside known area."
        )

        # Test the record against org_group2 rules.
        ok, messages = repo.run(record, org_group2.id)
        # It should fail unequivocally.
        assert ok is False
        assert len(messages) == 1
        assert messages[0] == (
            "organisation2:group2:tenkm: Record is outside known area."
        )
        # Change the record to taxon2 for which there are no rules.
        record.preferred_tvk = taxon2.preferred_tvk

        # Test the record against org_group1 rules.
        ok, messages = repo.run(record, org_group1.id)
        # It should baulk as no rule.
        assert ok is None
        assert len(messages) == 0

        # Test the record against all rules.
        ok, messages = repo.run(record)
        # It should baulk as no rule.
        assert ok is None
        assert len(messages) == 0
