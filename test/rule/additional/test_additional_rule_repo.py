import os

from sqlmodel import Session

from app.rule.additional.additional_rule_repo import AdditionalRuleRepo
from app.sqlmodels import OrgGroup, Taxon, AdditionalCode


class TestAdditionalCodeRepo:
    """Tests of the repo class."""

    def test_additional_rule_repo(self, session: Session):
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
        session.refresh(additional_code1)
        session.refresh(additional_code2)

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
