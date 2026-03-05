import json

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.settings_env import EnvSettings
from app.species.cache import (
    get_taxon_by_tvk, get_taxon_by_name, _get_taxon_by_tvk_wrapped
)

from ..mocks import mock_make_search_request


class TestSpeciesCache:
    def test_species_cache_by_tvk(self, client: TestClient, mocker):
        # Mock the Indicia warehouse.
        mocker.patch(
            'app.species.indicia.make_search_request',
            mock_make_search_request
        )

        # Test cache is table is empty.
        response = client.get("/species/cache/count")
        assert response.status_code == 200
        result = response.json()
        assert result['count'] == 0

        # Empty LRU Cache.
        # If the LRU cache contains this record already then it won't be added
        # to the cache table.
        _get_taxon_by_tvk_wrapped.cache_clear()

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

        # Test cache table is not empty.
        response = client.get("/species/cache/count")
        assert response.status_code == 200
        result = response.json()
        assert result['count'] == 1

        # Request cache table entry by id.
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

        # Delete cache table entry by id.
        response = client.delete("/species/cache/1")
        assert response.status_code == 200
        result = response.json()
        assert result['ok'] is True

        # Test cache table is empty.
        response = client.get("/species/cache/count")
        assert response.status_code == 200
        result = response.json()
        assert result['count'] == 0

        # Request species by invalid TVK.
        response = client.get("/species/cache/taxon_by_tvk/ABC123")
        assert response.status_code == 404
        result = json.loads(response.text)
        assert result['detail'] == 'TVK ABC123 not recognised.'

    def test_lru_cache_by_tvk(self, db: Session, env: EnvSettings, mocker):
        # Mock the Indicia warehouse.
        mocker.patch(
            'app.species.indicia.make_search_request',
            mock_make_search_request
        )
        # First request should look up taxon.
        taxon1 = get_taxon_by_tvk(db, env, 'NBNSYS0000008319')
        # Second request should hit LRU cache.
        taxon2 = get_taxon_by_tvk(db, env, 'NBNSYS0000008319')
        assert taxon1 == taxon2

    def test_lru_cache_by_name(self, db: Session, env: EnvSettings, mocker):
        # Mock the Indicia warehouse.
        mocker.patch(
            'app.species.indicia.make_search_request',
            mock_make_search_request
        )
        # First request should look up taxon.
        taxon1 = get_taxon_by_name(db, env, 'Adalia bipunctata')
        # Second request should hit LRU cache.
        taxon2 = get_taxon_by_name(db, env, 'Adalia bipunctata')
        assert taxon1 == taxon2
