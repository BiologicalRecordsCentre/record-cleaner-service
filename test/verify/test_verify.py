from fastapi.testclient import TestClient
from sqlmodel import Session

from app.sqlmodels import OrgGroup, Taxon, TenkmRule
from app.verify.verify_models import VerifyPack, OrgGroupRules

from ..mocks import mock_make_search_request


class TestVerify:

    def test_no_records(self, client: TestClient):
        pack = VerifyPack(
            records=[],
        )
        response = client.post(
            '/verify',
            json=pack.model_dump(),
        )
        assert response.status_code == 200
        assert response.json() == {
            "org_group_rules_list": None,
            "records": [],
        }

    def test_valid_record(self, client: TestClient, mocker, session: Session):
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
        verified = response.json()['records'][0]
        assert verified['name'] == "Adalia bipunctata"
        assert verified['date'] == "03/04/2024"
        assert verified['sref']['gridref'] == "TL123456"
        assert not verified['ok']
        assert len(verified['messages']) == 2
        assert verified['messages'][0] == (
            "*:*:phenology: There is no rule for this taxon.")
        assert verified['messages'][1] == (
            "*:*:tenkm: There is no rule for this taxon.")

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
        verified = response.json()['records'][0]
        assert len(verified['messages']) == 1
        assert verified['messages'][0] == (
            "Unrecognised organisation:group, 'UK Ladybird Survey:UKLS'.")

        # Create the missing org_group.
        org_group = OrgGroup(organisation='UK Ladybird Survey', group='UKLS')
        session.add(org_group)
        session.commit()
        # Now try again with that test.
        response = client.post(
            '/verify',
            json=pack.model_dump(),
        )
        assert response.status_code == 200
        verified = response.json()['records'][0]
        assert len(verified['messages']) == 2
        assert verified['messages'][0] == (
            "UK Ladybird Survey:UKLS:phenology: There is no rule for this taxon.")
        assert verified['messages'][1] == (
            "UK Ladybird Survey:UKLS:tenkm: There is no rule for this taxon.")

        # Update to test against specific rule.
        pack.org_group_rules_list[0].rules = ['tenkm']
        # Now try again with that test.
        response = client.post(
            '/verify',
            json=pack.model_dump(),
        )
        assert response.status_code == 200
        verified = response.json()['records'][0]
        assert len(verified['messages']) == 1
        assert verified['messages'][0] == (
            "UK Ladybird Survey:UKLS:tenkm: There is no rule for this taxon.")

        # Create a tenkm rule to test against.
        # Create taxa.
        taxon1 = Taxon(
            name='Adalia bipunctata',
            preferred_name='Adalia bipunctata',
            search_name='adaliabipunctata',
            tvk='NBNSYS0000008319',
            preferred_tvk='NBNSYS0000008319',
            preferred=True
        )
        session.add(taxon1)
        session.commit()

        # Create tenkm rule for org_group and taxon1.
        rule1 = TenkmRule(
            org_group_id=org_group.id,
            taxon_id=taxon1.id,
            km100='TL',
            km10='14',
            coord_system='OSGB'
        )
        session.add(rule1)
        session.commit()

        # Now try again with verification which should pass.
        response = client.post(
            '/verify',
            json=pack.model_dump(),
        )
        assert response.status_code == 200
        verified = response.json()['records'][0]
        assert len(verified['messages']) == 0
        assert verified['ok'] is True

        # Change the record location to be outside the tenkm rule.
        pack.records[0].sref.gridref = "TL 654 321"
        response = client.post(
            '/verify',
            json=pack.model_dump(),
        )
        assert response.status_code == 200
        verified = response.json()['records'][0]
        assert len(verified['messages']) == 1
        assert verified['messages'][0] == (
            "UK Ladybird Survey:UKLS:tenkm: Record is outside known area.")
        assert verified['ok'] is False
