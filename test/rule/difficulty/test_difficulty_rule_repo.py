import os

from sqlmodel import Session

from app.rule.difficulty.difficulty_rule_repo import DifficultyRuleRepo
from app.sqlmodels import OrgGroup, Taxon, DifficultyCode


class TestDifficultyRuleRepo:
    """Tests of the repo class."""

    def test_difficulty_rule_repo(self, session: Session):
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
        session.refresh(taxon1)
        session.refresh(taxon2)
        session.refresh(taxon3)

        # Create difficulty codes.
        difficulty_code1 = DifficultyCode(
            code=1,
            text='Easy',
            org_group_id=org_group1.id
        )
        difficulty_code2 = DifficultyCode(
            code=2,
            text='Hard',
            org_group_id=org_group2.id
        )
        session.add(difficulty_code1)
        session.add(difficulty_code2)
        session.commit()
        session.refresh(difficulty_code1)
        session.refresh(difficulty_code2)

        # Locate the directory of test data.
        thisdir = os.path.abspath(os.path.dirname(__file__))
        dir = os.path.join(thisdir, 'testdata')

        # Load a file.
        repo = DifficultyRuleRepo(session)
        errors = repo.load_file(
            dir, org_group1.id, 'abc123', 'id_difficulty_3.csv')
        assert (errors == [])

        # Check the results by org_group.
        result = repo.list_by_org_group(org_group1.id)
        assert len(result) == 3
        assert result[0]['tvk'] == taxon1.tvk
        assert result[0]['taxon'] == taxon1.name
        assert result[0]['difficulty'] == 1
        assert result[1]['tvk'] == taxon2.tvk
        assert result[1]['taxon'] == taxon2.name
        assert result[1]['difficulty'] == 1
        assert result[2]['tvk'] == taxon3.tvk
        assert result[2]['taxon'] == taxon3.name
        assert result[2]['difficulty'] == 1

        # Load a shorter file.
        errors = repo.load_file(
            dir, org_group1.id, 'xyz321', 'id_difficulty_1.csv')
        assert (errors == [])

        # Check the results by org_group.
        result = repo.list_by_org_group(org_group1.id)
        assert len(result) == 1
        assert result[0]['tvk'] == taxon1.tvk
        assert result[0]['taxon'] == taxon1.name
        assert result[0]['difficulty'] == 1

        # Load a difficulty rule of the same taxon to another org_group.
        errors = repo.load_file(
            dir, org_group2.id, 'pqr987', 'id_difficulty_1_2.csv')
        assert (errors == [])

        # Check the results by tvk.
        result = repo.list_by_tvk(taxon1.tvk)
        assert len(result) == 2
        assert result[0]['organisation'] == org_group1.organisation
        assert result[0]['group'] == org_group1.group
        assert result[0]['difficulty'] == difficulty_code1.code
        assert result[0]['text'] == difficulty_code1.text
        assert result[1]['organisation'] == org_group2.organisation
        assert result[1]['group'] == org_group2.group
        assert result[1]['difficulty'] == difficulty_code2.code
        assert result[1]['text'] == difficulty_code2.text

        # Delete org_group1.
        session.delete(org_group1)
        session.commit()

        # Check the deletion cascades.
        result = repo.list_by_tvk(taxon1.tvk)
        assert len(result) == 1
        assert result[0]['organisation'] == org_group2.organisation
        assert result[0]['group'] == org_group2.group
        assert result[0]['difficulty'] == difficulty_code2.code
