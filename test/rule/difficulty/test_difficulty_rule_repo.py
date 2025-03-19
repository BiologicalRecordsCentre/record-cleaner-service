import os

from sqlmodel import Session

from app.rule.difficulty.difficulty_rule_repo import DifficultyRuleRepo
from app.settings_env import EnvSettings
from app.sqlmodels import OrgGroup, Taxon, DifficultyCode, DifficultyRule
from app.utility.sref import Sref, SrefSystem
from app.utility.sref.sref_factory import SrefFactory
from app.verify.verify_models import Verified


class TestDifficultyRuleRepo:
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
        db.add(difficulty_code1)
        db.add(difficulty_code2)
        db.commit()
        db.refresh(difficulty_code1)
        db.refresh(difficulty_code2)

        # Locate the directory of test data.
        thisdir = os.path.abspath(os.path.dirname(__file__))
        dir = os.path.join(thisdir, 'testdata')

        # Load a file.
        repo = DifficultyRuleRepo(db, env)
        errors = repo.load_file(
            dir, org_group1.id, 'abc123', 'id_difficulty_3.csv')
        assert (errors == [])

        # Check the results by org_group.
        result = repo.list_by_org_group(org_group1.id)
        assert len(result) == 3
        assert result[0]['organism_key'] == 'NBNORG0000010513'
        assert result[0]['taxon'] == 'Adalia bipunctata'
        assert result[0]['difficulty'] == 1
        assert result[1]['organism_key'] == 'NBNORG0000010514'
        assert result[1]['taxon'] == 'Adalia decempunctata'
        assert result[1]['difficulty'] == 1
        assert result[2]['organism_key'] == 'NBNORG0000010517'
        assert result[2]['taxon'] == 'Coccinella quinquepunctata'
        assert result[2]['difficulty'] == 1

        # Load a shorter file.
        errors = repo.load_file(
            dir, org_group1.id, 'xyz321', 'id_difficulty_1.csv')
        assert (errors == [])

        # Check the results by org_group.
        result = repo.list_by_org_group(org_group1.id)
        assert len(result) == 1
        assert result[0]['organism_key'] == 'NBNORG0000010513'
        assert result[0]['taxon'] == 'Adalia bipunctata'
        assert result[0]['difficulty'] == 1

        # Load a difficulty rule of the same taxon to another org_group.
        errors = repo.load_file(
            dir, org_group2.id, 'pqr987', 'id_difficulty_1_2.csv')
        assert (errors == [])

        # Check the results by tvk.
        result = repo.list_by_organism_key('NBNORG0000010513')
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
        db.delete(org_group1)
        db.commit()

        # Check the deletion cascades.
        result = repo.list_by_organism_key('NBNORG0000010513')
        assert len(result) == 1
        assert result[0]['organisation'] == org_group2.organisation
        assert result[0]['group'] == org_group2.group
        assert result[0]['difficulty'] == difficulty_code2.code

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
        taxon2 = Taxon(
            name='Adalia decempunctata',
            preferred_name='Adalia decempunctata',
            search_name='adaliadecempunctata',
            tvk='NBNSYS0000008320',
            preferred_tvk='NBNSYS0000008320',
            preferred=True,
            organism_key='NBNORG0000010514',
        )
        db.add(taxon1)
        db.add(taxon2)
        db.commit()

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
        db.add(difficulty_code1)
        db.add(difficulty_code2)
        db.commit()

        # Create difficulty rules.
        # 2 rules for the same taxon in different org_groups.
        difficulty_rule1 = DifficultyRule(
            org_group_id=org_group1.id,
            organism_key=taxon1.organism_key,
            taxon=taxon1.name,
            difficulty_code_id=difficulty_code1.id
        )
        difficulty_rule2 = DifficultyRule(
            org_group_id=org_group2.id,
            organism_key=taxon1.organism_key,
            taxon=taxon1.name,
            difficulty_code_id=difficulty_code2.id
        )
        db.add(difficulty_rule1)
        db.add(difficulty_rule2)
        db.commit()

        # Create record of taxon1 to test.
        record = Verified(
            id=1,
            date='1/6/1975',
            sref=SrefFactory(
                Sref(gridref='TL1234', srid=SrefSystem.GB_GRID)
            ).value,
            organism_key=taxon1.organism_key
        )

        repo = DifficultyRuleRepo(db, env)

        # Test the record against all org_group rules.
        id_difficulty, messages = repo.run(record)
        # It should return two messages.
        assert id_difficulty == 2
        assert len(messages) == 2
        assert messages[0] == "organisation1:group1:difficulty:1: Easy"
        assert messages[1] == "organisation2:group2:difficulty:2: Hard"

        # Test the record against all org_group rules without messages.
        id_difficulty, messages = repo.run(record, False)
        # It should return no messages.
        assert id_difficulty == 2
        assert len(messages) == 0

        # Test the record against org_group1 rules.
        id_difficulty, messages = repo.run(record, True, org_group1.id)
        # It should return a single message.
        assert id_difficulty == 1
        assert len(messages) == 1
        assert messages[0] == "organisation1:group1:difficulty:1: Easy"

        # Change record to taxon2.
        record.organism_key = taxon2.organism_key
        # Test the record against all org_group rules.
        id_difficulty, messages = repo.run(record)
        # It should return nothing as there are no rules for the taxon.
        assert id_difficulty is None
        assert len(messages) == 0
