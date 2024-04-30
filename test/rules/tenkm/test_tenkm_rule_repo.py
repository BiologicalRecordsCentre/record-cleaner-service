import os

from sqlmodel import Session

from app.rules.tenkm.tenkm_rule_repo import TenkmRuleRepo
from app.sqlmodels import OrgGroup, Taxon


class TestTenkmRuleRepo:
    """Tests of the repo class."""

    def test_tenkm_rule_repo(self, session: Session):
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
