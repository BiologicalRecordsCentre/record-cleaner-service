from fastapi.testclient import TestClient


class TestCounty:

    def test_county_by_code(self, client: TestClient):
        # Valid code.
        response = client.get('/county/code/26')
        assert response.status_code == 200

        county = response.json()
        assert county['code'] == '26'
        assert county['name'] == 'West Suffolk'

        # Invalid code.
        response = client.get('/county/code/999')
        assert response.status_code == 404

    def test_county_by_gridref(self, client: TestClient):
        # Valid gridref.
        response = client.get('/county/gridref/TL123456')
        assert response.status_code == 200

        county = response.json()
        assert county['gridref'] == 'TL1245'
        assert county['code'] == '30'
        assert county['name'] == 'Bedfordshire'

        # Invalid gridref.
        response = client.get('/county/gridref/TM9999')
        assert response.status_code == 404

        # Irish gridref.
        response = client.get('/county/gridref/H30')
        assert response.status_code == 400

        # Channel Island gridref.
        response = client.get('/county/gridref/WV65')
        assert response.status_code == 400
