import os

from sqlmodel import Session

from app.rules.difficulty.difficulty_rule_repo import DifficultyRuleRepo
from app.sqlmodels import OrgGroup, Taxon, DifficultyCode


class TestDifficultyCodeRepo:

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
        assert (result == [
            {'tvk': taxon1.tvk, 'taxon': taxon1.name, 'difficulty': 1},
            {'tvk': taxon2.tvk, 'taxon': taxon2.name, 'difficulty': 1},
            {'tvk': taxon3.tvk, 'taxon': taxon3.name, 'difficulty': 1}
        ])

        # Load a shorter file.
        errors = repo.load_file(
            dir, org_group1.id, 'xyz321', 'id_difficulty_1.csv')
        assert (errors == [])

        # Check the results by org_group.
        result = repo.list_by_org_group(org_group1.id)
        assert (result == [
            {'tvk': taxon1.tvk, 'taxon': taxon1.name, 'difficulty': 1}
        ])

        # Load the same file to another org_group.
        errors = repo.load_file(
            dir, org_group2.id, 'pqr987', 'id_difficulty_1_2.csv')
        assert (errors == [])

        # Check the results by tvk.
        result = repo.list_by_tvk(taxon1.tvk)
        assert (result == [
            {
                'organisation': org_group1.organisation,
                'group': org_group1.group,
                'difficulty': difficulty_code1.code,
                'text': difficulty_code1.text
            },
            {
                'organisation': org_group2.organisation,
                'group': org_group2.group,
                'difficulty': difficulty_code2.code,
                'text': difficulty_code2.text
            }
        ])
