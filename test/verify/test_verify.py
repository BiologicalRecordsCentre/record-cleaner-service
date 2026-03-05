from datetime import datetime

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.sqlmodels import (
    OrgGroup,
    Taxon,
    TenkmRule,
    DifficultyCode,
    DifficultyRule
)
from app.verify.verify_models import VerifyPack, OrgGroupRules

from ..mocks import mock_make_search_request


class TestVerify:

    def test_no_records(self, client: TestClient):
        pack = VerifyPack(
            records=[],
        )
        # Use settings from client context to set rule metadata.
        settings = client.app.context['settings']
        settings.db.rules_commit = 'test123'
        settings.db.rules_update_time = '2026-02-23 16:59:59'

        response = client.post(
            '/verify',
            json=pack.model_dump(),
        )
        assert response.status_code == 200
        verified = response.json()
        assert verified['records'] == []
        assert verified['rules_commit'] == 'test123'
        assert verified['rules_update_time'] == '2026-02-23 16:59:59'

    def test_valid_record(self, client: TestClient, mocker):
        # Use settings from client context to set rule metadata.
        settings = client.app.context['settings']
        settings.db.rules_commit = 'test123'
        settings.db.rules_update_time = '2026-02-23 16:59:59'
        # Get database connection from client.
        engine = client.app.context['engine']
        with Session(engine) as db:
            # Mock the Indicia warehouse.
            mocker.patch(
                'app.species.indicia.make_search_request',
                mock_make_search_request
            )

            pack = VerifyPack(
                records=[{
                    "id": 1,
                    "date": "3/4/2024",
                    "sref": {
                        "srid": 0,
                        "gridref": "TL 123 456"
                    },
                    "tvk": "NBNSYS0000008319"
                }],
            )
            response = client.post(
                '/verify',
                json=pack.model_dump(),
            )
            assert response.status_code == 200
            verified = response.json()
            record = verified['records'][0]
            assert record['name'] == "Adalia bipunctata"
            assert record['date'] == "03/04/2024"
            assert record['sref']['gridref'] == "TL123456"
            assert record['result'] == 'warn'
            assert 'id_difficulty' not in record
            assert len(record['messages']) == 1
            assert record['messages'][0] == (
                "No rules exist for this taxon.")
            assert verified['rules_commit'] == 'test123'
            assert verified['rules_update_time'] == '2026-02-23 16:59:59'

            # Update to test against specific org_group.
            rules = OrgGroupRules(
                organisation="UK Ladybird Survey",
                group="UKLS",
            )
            pack.org_group_rules_list = [rules]
            response = client.post(
                '/verify',
                json=pack.model_dump(),
            )
            assert response.status_code == 200
            verified = response.json()
            record = verified['records'][0]
            assert record['result'] == 'fail'
            assert 'id_difficulty' not in record
            assert len(record['messages']) == 1
            assert record['messages'][0] == (
                "Unrecognised organisation:group, 'UK Ladybird Survey:UKLS'.")
            assert verified['rules_commit'] == 'test123'
            assert verified['rules_update_time'] == '2026-02-23 16:59:59'

            # Create the missing org_group.
            org_group = OrgGroup(
                organisation='UK Ladybird Survey', group='UKLS')
            db.add(org_group)
            db.commit()

            # Now try again with that test.
            response = client.post(
                '/verify',
                json=pack.model_dump(),
            )
            assert response.status_code == 200
            verified = response.json()
            record = verified['records'][0]
            assert record['result'] == 'warn'
            assert 'id_difficulty' not in record
            assert len(record['messages']) == 1
            assert record['messages'][0] == (
                "UK Ladybird Survey:UKLS: No rules exist for this taxon.")
            assert verified['rules_commit'] == 'test123'
            assert verified['rules_update_time'] == '2026-02-23 16:59:59'

            # Create the missing difficulty rule.
            # Create taxa.
            taxon = Taxon(
                name='Adalia bipunctata',
                preferred_name='Adalia bipunctata',
                search_name='adaliabipunctata',
                tvk='NBNSYS0000008319',
                preferred_tvk='NBNSYS0000008319',
                preferred=True,
                organism_key='NBNORG0000010513',
            )
            db.add(taxon)
            db.commit()
            db.refresh(taxon)

            # Create difficulty code.
            difficulty_code = DifficultyCode(
                code=1,
                text='Easy',
                org_group_id=org_group.id
            )
            db.add(difficulty_code)
            db.commit()
            db.refresh(difficulty_code)

            # Create difficulty rule.
            difficulty_rule = DifficultyRule(
                org_group_id=org_group.id,
                organism_key=taxon.organism_key,
                taxon=taxon.name,
                difficulty_code_id=difficulty_code.id
            )
            db.add(difficulty_rule)
            db.commit()

            # Now try again with that test.
            response = client.post(
                '/verify',
                json=pack.model_dump(),
            )
            assert response.status_code == 200
            verified = response.json()
            record = verified['records'][0]
            assert record['result'] == 'warn'
            assert record['id_difficulty'] == 1
            assert len(record['messages']) == 2
            assert record['messages'][0] == (
                "No rules run.")
            assert record['messages'][1] == (
                "UK Ladybird Survey:UKLS:difficulty:1: Easy")
            assert verified['rules_commit'] == 'test123'
            assert verified['rules_update_time'] == '2026-02-23 16:59:59'

            # Update to test against specific rule.
            pack.org_group_rules_list[0].rules = ['tenkm']
            # Now try again with that test.
            response = client.post(
                '/verify',
                json=pack.model_dump(),
            )
            assert response.status_code == 200
            verified = response.json()
            record = verified['records'][0]
            assert record['result'] == 'warn'
            assert record['id_difficulty'] == 1
            assert len(record['messages']) == 2
            assert record['messages'][0] == (
                "No rules run.")
            assert record['messages'][1] == (
                "UK Ladybird Survey:UKLS:difficulty:1: Easy")
            assert verified['rules_commit'] == 'test123'
            assert verified['rules_update_time'] == '2026-02-23 16:59:59'

            # Create a tenkm to test against.
            # Create tenkm rule for org_group and taxon.
            rule1 = TenkmRule(
                org_group_id=org_group.id,
                organism_key=taxon.organism_key,
                taxon=taxon.name,
                km100='TL',
                km10='14 15 16',
                coord_system='OSGB'
            )
            db.add(rule1)
            db.commit()

            # Now try again with verification which should pass.
            response = client.post(
                '/verify',
                json=pack.model_dump(),
            )
            assert response.status_code == 200
            verified = response.json()
            record = verified['records'][0]
            assert record['result'] == 'pass'
            assert record['id_difficulty'] == 1
            assert len(record['messages']) == 2
            assert record['messages'][0] == (
                'Rules run: tenkm')
            assert record['messages'][1] == (
                'UK Ladybird Survey:UKLS:difficulty:1: Easy')
            assert verified['rules_commit'] == 'test123'
            assert verified['rules_update_time'] == '2026-02-23 16:59:59'

            # Now try again with verbose = 0.
            response = client.post(
                '/verify',
                params={'verbose': '0'},
                json=pack.model_dump(),
            )
            assert response.status_code == 200
            verified = response.json()
            record = verified['records'][0]
            assert record['result'] == 'pass'
            assert record['id_difficulty'] == 1
            assert len(record['messages']) == 1
            assert record['messages'][0] == (
                'Rules run: tenkm')
            assert verified['rules_commit'] == 'test123'
            assert verified['rules_update_time'] == '2026-02-23 16:59:59'

            # Change record location to outside the tenkm rule - should fail.
            pack.records[0].sref.gridref = "TL 654 321"
            response = client.post(
                '/verify',
                json=pack.model_dump(),
            )
            assert response.status_code == 200
            verified = response.json()
            record = verified['records'][0]
            assert record['result'] == 'fail'
            assert record['id_difficulty'] == 1
            assert len(record['messages']) == 2
            assert record['messages'][0] == (
                'UK Ladybird Survey:UKLS:difficulty:1: Easy')
            assert record['messages'][1] == (
                "UK Ladybird Survey:UKLS:tenkm: Location is outside known "
                "distribution.")
            assert verified['rules_commit'] == 'test123'
            assert verified['rules_update_time'] == '2026-02-23 16:59:59'

            # Remove the rule list - should still fail.
            pack.org_group_rules_list = []
            response = client.post(
                '/verify',
                json=pack.model_dump(),
            )
            assert response.status_code == 200
            verified = response.json()
            record = verified['records'][0]
            assert record['result'] == 'fail'
            assert record['id_difficulty'] == 1
            assert len(record['messages']) == 2
            assert record['messages'][0] == (
                'UK Ladybird Survey:UKLS:difficulty:1: Easy')
            assert record['messages'][1] == (
                "UK Ladybird Survey:UKLS:tenkm: Location is outside known "
                "distribution.")
            assert verified['rules_commit'] == 'test123'
            assert verified['rules_update_time'] == '2026-02-23 16:59:59'

            # Put two records in the pack.
            record = pack.records[0]
            pack.records.append(record)
            response = client.post(
                '/verify',
                json=pack.model_dump(),
            )
            assert response.status_code == 200
            verified = response.json()
            assert len(verified['records']) == 2

            # Check usage
            year = datetime.now().year
            response = client.get(f"/usage/{year}")
            assert response.status_code == 200
            usages = response.json()
            assert len(usages) == 1
            usage = usages[0]
            assert usage['user_name'] == 'Tom'
            assert usage['verification_requests'] == 10
            assert usage['validation_requests'] == 0
            assert usage['verification_records'] == 11
            assert usage['validation_records'] == 0
