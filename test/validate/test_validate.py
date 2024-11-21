from fastapi.testclient import TestClient

from ..mocks import mock_make_search_request


class TestValidate:

    def test_no_records(self, client: TestClient):
        response = client.post(
            "/validate",
            json=[]
        )
        assert response.status_code == 200
        assert response.json() == []

    def test_empty_record(self, client: TestClient):
        response = client.post(
            "/validate",
            json=[{}]
        )
        assert response.status_code == 422

    def test_null_record(self, client: TestClient):
        response = client.post(
            "/validate",
            json=[{
                "id": None,
                "date": None,
                "sref": None,
            }]
        )
        assert response.status_code == 422

    def test_invlaid_srid(self, client: TestClient):
        response = client.post(
            "/validate",
            json=[{
                "id": 1,
                "date": "",
                "sref": {"srid": 123},
            }]
        )
        assert response.status_code == 422

    def test_syntactically_valid_record(self, client: TestClient, mocker):
        # Mock the Indicia warehouse.
        mocker.patch(
            'app.species.indicia.make_search_request',
            mock_make_search_request
        )

        response = client.post(
            "/validate",
            json=[{
                "id": 1,
                "date": "",
                "sref": {"srid": 0},
            }]
        )
        assert response.status_code == 200
        validated = response.json()[0]
        assert not validated['ok']
        assert validated['messages'][0] == "TVK or name required."
        assert validated['messages'][1] == "Unrecognised date format."
        assert validated['messages'][2] == "Invalid spatial reference. A gridref must be provided."

    def test_valid_record_accepted_tvk(self, client: TestClient, mocker):
        # Mock the Indicia warehouse.
        mocker.patch(
            'app.species.indicia.make_search_request',
            mock_make_search_request
        )

        response = client.post(
            "/validate",
            json=[{
                "id": 1,
                "date": "3/4/2024",
                "sref": {
                    "srid": 0,
                    "gridref": "TL 123 456"
                },
                "tvk": "NBNSYS0000008319"
            }]
        )
        assert response.status_code == 200
        validated = response.json()[0]
        assert validated['name'] == "Adalia bipunctata"
        assert validated['date'] == "03/04/2024"
        assert validated['sref']['gridref'] == "TL123456"
        assert validated['preferred_tvk'] == "NBNSYS0000008319"
        assert validated['ok']
        assert len(validated['messages']) == 0

    def test_valid_record_common_tvk(self, client: TestClient, mocker):
        # Mock the Indicia warehouse.
        mocker.patch(
            'app.species.indicia.make_search_request',
            mock_make_search_request
        )

        response = client.post(
            "/validate",
            json=[{
                "id": 1,
                "date": "3/4/2024",
                "sref": {
                    "srid": 0,
                    "gridref": "TL 123 456"
                },
                "tvk": "NBNSYS0000171481"
            }]
        )
        assert response.status_code == 200
        validated = response.json()[0]
        assert validated['name'] == "Two-Spot Ladybird"
        assert validated['date'] == "03/04/2024"
        assert validated['sref']['gridref'] == "TL123456"
        assert validated['preferred_tvk'] == "NBNSYS0000008319"
        assert validated['ok']
        assert len(validated['messages']) == 0

    def test_valid_record_accepted_name(self, client: TestClient, mocker):
        # Mock the Indicia warehouse.
        mocker.patch(
            'app.species.indicia.make_search_request',
            mock_make_search_request
        )

        response = client.post(
            "/validate",
            json=[{
                "id": 1,
                "date": "3/4/2024",
                "sref": {
                    "srid": 0,
                    "gridref": "TL 123 456"
                },
                "name": "Adalia bipunctata"
            }]
        )
        assert response.status_code == 200
        validated = response.json()[0]
        assert validated['date'] == "03/04/2024"
        assert validated['sref']['gridref'] == "TL123456"
        assert validated['preferred_tvk'] == "NBNSYS0000008319"
        assert validated['ok']
        assert len(validated['messages']) == 0

    def test_valid_record_common_name(self, client: TestClient, mocker):
        # Mock the Indicia warehouse.
        mocker.patch(
            'app.species.indicia.make_search_request',
            mock_make_search_request
        )

        response = client.post(
            "/validate",
            json=[{
                "id": 1,
                "date": "3/4/2024",
                "sref": {
                    "srid": 0,
                    "gridref": "TL 123 456"
                },
                "name": "Two-Spot Ladybird"
            }]
        )
        assert response.status_code == 200
        validated = response.json()[0]
        assert validated['date'] == "03/04/2024"
        assert validated['sref']['gridref'] == "TL123456"
        assert validated['preferred_tvk'] == "NBNSYS0000008319"
        assert validated['ok']
        assert len(validated['messages']) == 0

    def test_invalid_vc(self, client: TestClient, mocker):
        # Mock the Indicia warehouse.
        mocker.patch(
            'app.species.indicia.make_search_request',
            mock_make_search_request
        )

        response = client.post(
            "/validate",
            json=[{
                "id": 1,
                "date": "3/4/2024",
                "sref": {
                    "srid": 0,
                    "gridref": "TL 123 456"
                },
                "tvk": "NBNSYS0000008319",
                "vc": 1
            }]
        )
        assert response.status_code == 200
        validated = response.json()[0]
        assert validated['name'] == "Adalia bipunctata"
        assert validated['date'] == "03/04/2024"
        assert validated['sref']['gridref'] == "TL123456"
        assert validated['vc'] == "1"
        assert not validated['ok']
        assert validated['messages'][0] == "Sref not in vice county."

    def test_valid_vc(self, client: TestClient, mocker):
        # Mock the Indicia warehouse.
        mocker.patch(
            'app.species.indicia.make_search_request',
            mock_make_search_request
        )

        response = client.post(
            "/validate",
            json=[{
                "id": 1,
                "date": "3/4/2024",
                "sref": {
                    "srid": 0,
                    "gridref": "TL 123 456"
                },
                "tvk": "NBNSYS0000008319",
                "vc": "Bedfordshire"
            }]
        )
        assert response.status_code == 200
        validated = response.json()[0]
        assert validated['name'] == "Adalia bipunctata"
        assert validated['date'] == "03/04/2024"
        assert validated['sref']['gridref'] == "TL123456"
        assert validated['vc'] == "30"
        assert validated['ok']
        assert len(validated['messages']) == 0

    def test_vc_assignment(self, client: TestClient, mocker):
        # Mock the Indicia warehouse.
        mocker.patch(
            'app.species.indicia.make_search_request',
            mock_make_search_request
        )

        response = client.post(
            "/validate",
            json=[{
                "id": 1,
                "date": "3/4/2024",
                "sref": {
                    "srid": 0,
                    "gridref": "TL 123 456"
                },
                "tvk": "NBNSYS0000008319"
            }]
        )
        assert response.status_code == 200
        validated = response.json()[0]
        assert validated['name'] == "Adalia bipunctata"
        assert validated['date'] == "03/04/2024"
        assert validated['sref']['gridref'] == "TL123456"
        assert validated['vc'] == "30"
        assert validated['ok']
        assert len(validated['messages']) == 0

    def test_vc_no_assignment(self, client: TestClient, mocker):
        # Mock the Indicia warehouse.
        mocker.patch(
            'app.species.indicia.make_search_request',
            mock_make_search_request
        )

        response = client.post(
            "/validate",
            json=[{
                "id": 1,
                "date": "3/4/2024",
                "sref": {
                    "srid": 0,
                    "gridref": "TM 999 999"
                },
                "tvk": "NBNSYS0000008319"
            }]
        )
        assert response.status_code == 200
        validated = response.json()[0]
        assert validated['name'] == "Adalia bipunctata"
        assert validated['date'] == "03/04/2024"
        assert validated['sref']['gridref'] == "TM999999"
        assert validated['vc'] == '0'
        assert validated['ok']
        assert len(validated['messages']) == 1
        assert validated['messages'][0] == "No vice county found for gridref."
