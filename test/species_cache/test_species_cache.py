import json

from fastapi.testclient import TestClient

from ..mocks import mock_make_search_request


class TestSpeciesCache:
    def test_species_cacheby_tvk(self, client: TestClient, mocker):
        # Mock the Indicia warehouse.
        mocker.patch(
            'app.species.indicia.make_search_request',
            mock_make_search_request
        )

        # Test cache is empty.
        response = client.get("/species/cache/count")
        assert response.status_code == 200
        result = response.json()
        assert result['count'] == 0

        # Request species by TVK.
        response = client.get("/species/cache/taxon_by_tvk/NBNSYS0000008319")
        assert response.status_code == 200
        taxon = response.json()
        assert taxon['search_name'] == "adaliabipunctata"
        assert taxon['tvk'] == "NBNSYS0000008319"
        assert taxon['id'] == 1
        assert taxon['name'] == "Adalia bipunctata"
        assert taxon['preferred'] is True
        assert taxon['preferred_name'] == "Adalia bipunctata"
        assert taxon['preferred_tvk'] == "NBNSYS0000008319"
        assert taxon['organism_key'] == "NBNORG0000010513"

        # Test cache is not empty.
        response = client.get("/species/cache/count")
        assert response.status_code == 200
        result = response.json()
        assert result['count'] == 1

        # Request cache entry by id.
        response = client.get("/species/cache/1")
        assert response.status_code == 200
        taxon = response.json()
        assert taxon['search_name'] == "adaliabipunctata"
        assert taxon['tvk'] == "NBNSYS0000008319"
        assert taxon['id'] == 1
        assert taxon['name'] == "Adalia bipunctata"
        assert taxon['preferred'] is True
        assert taxon['preferred_name'] == "Adalia bipunctata"
        assert taxon['preferred_tvk'] == "NBNSYS0000008319"
        assert taxon['organism_key'] == "NBNORG0000010513"

        # Delete cache entry by id.
        response = client.delete("/species/cache/1")
        assert response.status_code == 200
        result = response.json()
        assert result['ok'] is True

        # Test cache is empty.
        response = client.get("/species/cache/count")
        assert response.status_code == 200
        result = response.json()
        assert result['count'] == 0

        # Request species by invalid TVK.
        response = client.get("/species/cache/taxon_by_tvk/ABC123")
        assert response.status_code == 404
        result = json.loads(response.text)
        assert result['detail'] == 'TVK ABC123 not recognised.'
