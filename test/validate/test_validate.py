from fastapi.testclient import TestClient

import app.auth as auth
from app.main import app
from app.sqlmodels import User

from ..mocks import mock_make_search_request


class TestValidateByTvk:

    def test_no_records(self, client: TestClient):
        response = client.post(
            "/validate/records_by_tvk",
            json=[]
        )
        assert response.status_code == 200
        assert response.json() == []

    def test_empty_record(self, client: TestClient):
        response = client.post(
            "/validate/records_by_tvk",
            json=[{}]
        )
        assert response.status_code == 422

    def test_null_record(self, client: TestClient):
        response = client.post(
            "/validate/records_by_tvk",
            json=[{
                "id": None,
                "date": None,
                "sref": None,
                "tvk": None
            }]
        )
        assert response.status_code == 422

    def test_invlaid_srid(self, client: TestClient):
        response = client.post(
            "/validate/records_by_tvk",
            json=[{
                "id": 1,
                "date": "",
                "sref": {"srid": 123},
                "tvk": "x"
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
            "/validate/records_by_tvk",
            json=[{
                "id": 1,
                "date": "",
                "sref": {"srid": 0},
                "tvk": "x"
            }]
        )
        assert response.status_code == 200
        assert not response.json()[0]['ok']
        assert response.json()[0]['message'] == "TVK not recognised."

    def test_valid_tvk(self, client: TestClient, mocker):
        # Mock the Indicia warehouse.
        mocker.patch(
            'app.species.indicia.make_search_request',
            mock_make_search_request
        )

        response = client.post(
            "/validate/records_by_tvk",
            json=[{
                "id": 1,
                "date": "",
                "sref": {"srid": 0},
                "tvk": "NBNSYS0000008319"
            }]
        )
        assert response.status_code == 200
        assert response.json()[0]['name'] == "Adalia bipunctata"
        assert not response.json()[0]['ok']
        assert response.json()[0]['message'] == "Unreocognised date format."

    def test_valid_date(self, client: TestClient, mocker):
        # Mock the Indicia warehouse.
        mocker.patch(
            'app.species.indicia.make_search_request',
            mock_make_search_request
        )

        response = client.post(
            "/validate/records_by_tvk",
            json=[{
                "id": 1,
                "date": "3/4/2024",
                "sref": {"srid": 0},
                "tvk": "NBNSYS0000008319"
            }]
        )
        assert response.status_code == 200
        assert response.json()[0]['name'] == "Adalia bipunctata"
        assert response.json()[0]['date'] == "03/04/2024"
        assert not response.json()[0]['ok']
        assert response.json()[0]['message'] == (
            "Invalid spatial reference. A gridref must be provided.")

    def test_valid_gridref(self, client: TestClient, mocker):
        # Mock the Indicia warehouse.
        mocker.patch(
            'app.species.indicia.make_search_request',
            mock_make_search_request
        )

        response = client.post(
            "/validate/records_by_tvk",
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
        assert response.json()[0]['name'] == "Adalia bipunctata"
        assert response.json()[0]['date'] == "03/04/2024"
        assert response.json()[0]['sref']['gridref'] == "TL123456"
        assert response.json()[0]['ok']
        assert response.json()[0]['message'] is None

    def test_invalid_vc(self, client: TestClient, mocker):
        # Mock the Indicia warehouse.
        mocker.patch(
            'app.species.indicia.make_search_request',
            mock_make_search_request
        )

        response = client.post(
            "/validate/records_by_tvk",
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
        assert response.json()[0]['name'] == "Adalia bipunctata"
        assert response.json()[0]['date'] == "03/04/2024"
        assert response.json()[0]['sref']['gridref'] == "TL123456"
        assert response.json()[0]['vc'] == "1"
        assert not response.json()[0]['ok']
        assert response.json()[0]['message'] == "Sref not in vice county."

    def test_valid_vc(self, client: TestClient, mocker):
        # Mock the Indicia warehouse.
        mocker.patch(
            'app.species.indicia.make_search_request',
            mock_make_search_request
        )

        response = client.post(
            "/validate/records_by_tvk",
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
        assert response.json()[0]['name'] == "Adalia bipunctata"
        assert response.json()[0]['date'] == "03/04/2024"
        assert response.json()[0]['sref']['gridref'] == "TL123456"
        assert response.json()[0]['vc'] == "30"
        assert response.json()[0]['ok']
