import os

from sqlmodel import Session

from app.rule.additional.additional_rule_repo import AdditionalRuleRepo
from app.sqlmodels import OrgGroup, Taxon, AdditionalCode, AdditionalRule
from app.utility.sref import Sref, SrefSystem
from app.verify.verify_models import Verified


class TestAdditionalRuleRepo:
    """Tests of the repo class."""

    def test_load_file(self, session: Session):
        # Create org_groups.
        org_group1 = OrgGroup(organisation='organisation1', group='group1')
        org_group2 = OrgGroup(organisation='organisation2', group='group2')
        session.add(org_group1)
        session.add(org_group2)
        session.commit()

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
        session.add(taxon1)
        session.add(taxon2)
        session.add(taxon3)
        session.commit()

        # Create additional codes.
        additional_code1 = AdditionalCode(
            code=1,
            text='Rare',
            org_group_id=org_group1.id
        )
        additional_code2 = AdditionalCode(
            code=2,
            text='Unknown',
            org_group_id=org_group2.id
        )
        session.add(additional_code1)
        session.add(additional_code2)
        session.commit()

        # Locate the directory of test data.
        thisdir = os.path.abspath(os.path.dirname(__file__))
        dir = os.path.join(thisdir, 'testdata')

        # Load a file.
        repo = AdditionalRuleRepo(session)
        errors = repo.load_file(
            dir, org_group1.id, 'abc123', 'additional_3.csv')
        assert (errors == [])

        # Check the results by org_group.
        result = repo.list_by_org_group(org_group1.id)
        assert len(result) == 3
        assert result[0]['tvk'] == taxon1.tvk
        assert result[0]['taxon'] == taxon1.name
        assert result[0]['code'] == 1
        assert result[1]['tvk'] == taxon2.tvk
        assert result[1]['taxon'] == taxon2.name
        assert result[1]['code'] == 1
        assert result[2]['tvk'] == taxon3.tvk
        assert result[2]['taxon'] == taxon3.name
        assert result[2]['code'] == 1

        # Load a shorter file.
        errors = repo.load_file(
            dir, org_group1.id, 'xyz321', 'additional_1.csv')
        assert (errors == [])

        # Check the results by org_group.
        result = repo.list_by_org_group(org_group1.id)
        assert len(result) == 1
        assert result[0]['tvk'] == taxon1.tvk
        assert result[0]['taxon'] == taxon1.name
        assert result[0]['code'] == 1

        # Load another additional rule of the same taxon to another org_group.
        errors = repo.load_file(
            dir, org_group2.id, 'pqr987', 'additional_1_2.csv')
        assert (errors == [])

        # Check the results by tvk.
        result = repo.list_by_tvk(taxon1.tvk)
        assert len(result) == 2
        assert result[0]['organisation'] == org_group1.organisation
        assert result[0]['group'] == org_group1.group
        assert result[0]['code'] == additional_code1.code
        assert result[0]['text'] == additional_code1.text
        assert result[1]['organisation'] == org_group2.organisation
        assert result[1]['group'] == org_group2.group
        assert result[1]['code'] == additional_code2.code
        assert result[1]['text'] == additional_code2.text

        # Delete org_group1.
        session.delete(org_group1)
        session.commit()

        # Check the deletion cascades.
        result = repo.list_by_tvk(taxon1.tvk)
        assert len(result) == 1
        assert result[0]['organisation'] == org_group2.organisation
        assert result[0]['group'] == org_group2.group
        assert result[0]['code'] == additional_code2.code

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
        session.add(taxon1)
        session.add(taxon2)
        session.commit()

        # Create additional codes for org_group1 and org_group2.
        code1 = AdditionalCode(
            code=1,
            text='Rare',
            org_group_id=org_group1.id
        )
        code2 = AdditionalCode(
            code=1,
            text='Scarce',
            org_group_id=org_group2.id
        )
        session.add(code1)
        session.add(code2)
        session.commit()

        # Create additional rule for org_group1 and taxon1.
        rule1 = AdditionalRule(
            org_group_id=org_group1.id,
            taxon_id=taxon1.id,
            additional_code_id=code1.id
        )
        # Create additional rule for org_group2 and taxon1.
        rule2 = AdditionalRule(
            org_group_id=org_group2.id,
            taxon_id=taxon1.id,
            additional_code_id=code2.id
        )
        session.add(rule1)
        session.add(rule2)
        session.commit()

        # Create record of taxon1 to test.
        record = Verified(
            id=1,
            date='23/5/2024',
            sref=Sref(gridref='TL123456', srid=SrefSystem.GB_GRID),
            tvk=taxon1.tvk
        )

        repo = AdditionalRuleRepo(session)

        # Test the record against rules for org_group1.
        failures = repo.run(record, org_group1.id)
        assert len(failures) == 1
        assert failures[0] == 'organisation1:group1:additional: Rare'

        # Test the record against rules for all org_groups.
        failures = repo.run(record)
        assert len(failures) == 2
        assert failures[0] == 'organisation1:group1:additional: Rare'
        assert failures[1] == 'organisation2:group2:additional: Scarce'

        # Change record to taxon2 which has no additional rules.
        record.tvk = taxon2.tvk
        failures = repo.run(record)
        assert len(failures) == 0
