import json

from fastapi.testclient import TestClient

from ..mocks import mock_make_search_request


class TestSpecies:
    def test_species_by_tvk(self, client: TestClient, mocker):
        # Mock the Indicia warehouse.
        mocker.patch(
            'app.species.indicia.make_search_request',
            mock_make_search_request
        )

        # Request species by TVK.
        response = client.get("/species/taxon_by_tvk/NBNSYS0000008319")
        assert response.status_code == 200
        taxon = response.json()
        assert taxon['name'] == "Adalia bipunctata"
        assert taxon['preferred_tvk'] == "NBNSYS0000008319"
        assert taxon['preferred_name'] == "Adalia bipunctata"
        assert taxon['tvk'] == "NBNSYS0000008319"
        assert taxon['organism_key'] == "NBNORG0000010513"

        # Request species by invalid TVK.
        response = client.get("/species/taxon_by_tvk/ABC123")
        assert response.status_code == 404
        result = json.loads(response.text)
        assert result['detail'] == 'TVK ABC123 not recognised.'

    def test_species_by_name(self, client: TestClient, mocker):
        # Mock the Indicia warehouse.
        mocker.patch(
            'app.species.indicia.make_search_request',
            mock_make_search_request
        )

        # Request species by name.
        response = client.get("/species/taxon_by_name/Adalia bipunctata")
        assert response.status_code == 200
        taxon = response.json()
        assert taxon['name'] == "Adalia bipunctata"
        assert taxon['preferred_tvk'] == "NBNSYS0000008319"
        assert taxon['preferred_name'] == "Adalia bipunctata"
        assert taxon['tvk'] == "NBNSYS0000008319"
        assert taxon['organism_key'] == "NBNORG0000010513"

        # Request species by invalid name.
        response = client.get("/species/taxon_by_name/Bidalia adpunctata")
        assert response.status_code == 404
        result = json.loads(response.text)
        assert result['detail'] == 'Name Bidalia adpunctata not recognised.'

        # Request mal-formed species by name.
        response = client.get("/species/taxon_by_name/Argynnis aglaja")
        assert response.status_code == 404
        result = json.loads(response.text)
        assert result['detail'] == 'Name Argynnis aglaja not recognised.'
