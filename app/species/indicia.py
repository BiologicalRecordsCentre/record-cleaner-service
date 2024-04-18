import hmac
import json
import requests
from enum import Enum
from typing import Annotated, Optional

from fastapi import APIRouter, Query, HTTPException, status
from pydantic import BaseModel

from app.settings import settings
import app.auth as auth
from app.sqlmodels import Taxon

router = APIRouter()


class IncludeParam(str, Enum):
    """Defines options available for the include parameter."""
    DATA = "data"
    COUNT = "count"
    PAGING = "paging"
    COLUMNS = "columns"


class IndiciaTaxon(BaseModel):
    taxa_taxon_list_id: int
    searchterm: str
    highlighted: Optional[str] = None
    taxon: str
    language_iso: str
    preferred_taxon: str
    preferred_authority: str
    default_common_name: Optional[str] = None
    taxon_group: str
    preferred: bool
    preferred_taxa_taxon_list_id: int
    taxon_meaning_id: int
    external_key: str
    organism_key: str
    taxon_group_id: int
    parent_id: int
    taxon_rank: str


class IndiciaResponse(BaseModel):
    data: list[IndiciaTaxon] | None = None
    count: int | None = None
    paging: dict | None = None
    columns: dict | None = None


class IndiciaAuth(requests.auth.AuthBase):
    """A nice way for requests to add Indicia authentication."""

    def __init__(self, password):
        self.password = password

    def __call__(self, r):
        key = self.password.encode('utf-8')
        msg = (r.url).encode('utf-8')
        hash = hmac.new(key, msg, 'sha1').hexdigest()
        auth = f'USER:{settings.indicia_rest_user}:HMAC:{hash}'
        r.headers['Authorization'] = auth
        return r


@router.get(
    '/species/indicia/taxon',
    tags=['Indicia'],
    summary="Search Indicia for taxa matching your parameters.",
    response_model=IndiciaResponse)
async def search_taxa(
    auth: auth.Auth,
    searchQuery: Annotated[
        str,
        Query(description="Search text which will be used to look up species "
              "and taxon names.")
    ] = None,
    taxon_group_id: Annotated[
        list[int],
        Query(description="List of IDs of taxon groups to limit the search "
              "to.")
    ] = None,
    taxon_group: Annotated[
        list[str],
        Query(description="List of taxon group names to limit the search to. "
              "An alternative to using taxon_group_id.")
    ] = None,
    scratchpad_list_id: Annotated[
        list[int],
        Query(description="List of IDs of taxa_taxon_list-related scratchpads "
              "to limit the search to.")
    ] = None,
    taxon_meaning_id: Annotated[
        list[int],
        Query(description="List of IDs of taxon meanings to limit the search "
              "to.")
    ] = None,
    taxa_taxon_list_id: Annotated[
        list[int],
        Query(description="List of IDs of taxa taxon list records to limit the "
              "search to.")
    ] = None,
    preferred_taxa_taxon_list_id: Annotated[
        list[int],
        Query(description="List of IDs of taxa taxon list records to limit "
              "the search to, using the preferred name's ID to filter "
              "against, therefore including synonyms and common names in the "
              "response.")
    ] = None,
    preferred_taxon: Annotated[
        list[str],
        Query(description="List of preferred names to limit the search to "
              "(e.g. limit to a list of species names). Exact matches "
              "required.")
    ] = None,
    external_key: Annotated[
        list[str],
        Query(description="List of UKSI TVKs to limit the search to, using "
              "the preferred name's TVK to filter against, therefore including "
              "synonyms and common names in the response.")
    ] = None,
    parent_id: Annotated[
        list[int],
        Query(description="List of IDs of taxa_taxon_list records to limit "
              "the search to children of, e.g. a species when searching the "
              "subspecies. May be set to 0 to force top level species only.")
    ] = None,
    language: Annotated[
        list[str],
        Query(description="List of Languages of names to include in search "
              "results. Pass a 3 character iso code for the language, e.g. "
              "'lat' for Latin names or 'eng' for English names. "
              "Alternatively set this to 'common' to filter for all common "
              "names (i.e. non-Latin names).")
    ] = None,
    preferred: Annotated[
        bool,
        Query(description="Set to true to limit to preferred names, false to "
              "limit to non-preferred names.")
    ] = None,
    commonNames: Annotated[
        bool,
        Query(description="Set to true to limit to common names, false to "
              "exclude common names.")
    ] = None,
    synonyms: Annotated[
        bool,
        Query(description="Set to true to limit to syonyms, false to exclude "
              "synonyms.")
    ] = None,
    abbreviations: Annotated[
        bool,
        Query(description="Set to false to disable searching 2+3 character "
              "species name abbreviations.")
    ] = None,
    marine_flag: Annotated[
        bool,
        Query(description="Set to true for only marine associated species, "
              "false to exclude marine-associated species.")
    ] = None,
    freshwater_flag: Annotated[
        bool,
        Query(description="Set to true for only freshwater associated "
              "species, false to exclude freshwater-associated species.")
    ] = None,
    terrestrial_flag: Annotated[
        bool,
        Query(description="Set to true for only terrestrial associated "
              "species, false to exclude terrestrial-associated species.")
    ] = None,
    non_native_flag: Annotated[
        bool,
        Query(description="Set to true for only non-native species, false to "
              "exclude non-native species.")
    ] = None,
    searchAuthors: Annotated[
        bool,
        Query(description="Set to true to include author strings in the "
              "searched text.")
    ] = None,
    wholeWords: Annotated[
        bool,
        Query(description="Set to true to only search whole words in the full "
              "text index, otherwise searches the start of words.")
    ] = None,
    min_taxon_rank_sort_order: Annotated[
        int,
        Query(description="Set to the minimum sort order of the taxon ranks "
              "to include in the results.")
    ] = None,
    max_taxon_rank_sort_order: Annotated[
        int,
        Query(description="Set to the maximum sort order of the taxon ranks "
              "to include in the results.")
    ] = None,
    limit: Annotated[
        int,
        Query(description="Limit the number of records in the response.")
    ] = 10,
    offset: Annotated[
        int,
        Query(description="Offset from the start of the dataset that the "
              "response will start.")
    ] = 0,
    include: Annotated[
        list[IncludeParam],
        Query(description="Defines which parts of the response structure to "
              "include. If the count and paging data are not required then "
              "exclude them for better performance. Options available are "
              "['data','count','paging','columns'].")
    ] = None
):
    """This is a proxy to the Indicia taxa/search API, limited to searcing
    the UK Species Inventory.

    Many of the parameters require you to have a knowledge of the species list
    present on the warehouse you are connected to.
    """

    params = {}
    if searchQuery:
        params['searchQuery'] = searchQuery
    if taxon_group_id:
        params['taxon_group_id'] = json.dumps(taxon_group_id)
    if taxon_group:
        params['taxon_group'] = json.dumps(taxon_group)
    if scratchpad_list_id:
        params['scratchpad_list_id'] = json.dumps(scratchpad_list_id)
    if taxon_meaning_id:
        params['taxon_meaning_id'] = json.dumps(taxon_meaning_id)
    if taxa_taxon_list_id:
        params['taxa_taxon_list_id'] = json.dumps(taxa_taxon_list_id)
    if preferred_taxa_taxon_list_id:
        params['preferred_taxa_taxon_list_id'] = json.dumps(
            preferred_taxa_taxon_list_id)
    if preferred_taxon:
        params['preferred_taxon'] = json.dumps(preferred_taxon)
    if external_key:
        params['external_key'] = json.dumps(external_key)
    if parent_id:
        params['parent_id'] = json.dumps(parent_id)
    if language:
        params['language'] = json.dumps(language)
    if preferred is not None:
        params['preferred'] = 'true' if preferred else 'false'
    if commonNames is not None:
        params['commonNames'] = 'true' if commonNames else 'false'
    if synonyms is not None:
        params['synonyms'] = 'true' if synonyms else 'false'
    if abbreviations:
        params['abbreviations'] = 'true' if abbreviations else 'false'
    if marine_flag is not None:
        params['marine_flag'] = 'true' if marine_flag else 'false'
    if freshwater_flag is not None:
        params['freshwater_flag'] = 'true' if freshwater_flag else 'false'
    if terrestrial_flag is not None:
        params['terrestrial_flag'] = 'true' if terrestrial_flag else 'false'
    if non_native_flag is not None:
        params['non_native_flag'] = 'true' if non_native_flag else 'false'
    if searchAuthors is not None:
        params['searchAuthors'] = 'true' if searchAuthors else 'false'
    if wholeWords is not None:
        params['wholeWords'] = 'true' if wholeWords else 'false'
    if min_taxon_rank_sort_order is not None:
        params['min_taxon_rank_sort_order'] = min_taxon_rank_sort_order
    if max_taxon_rank_sort_order is not None:
        params['max_taxon_rank_sort_order'] = max_taxon_rank_sort_order
    if limit is not None:
        params['limit'] = limit
    if offset is not None:
        params['offset'] = offset
    if include:
        # Convert the list of IncludeParam to a list of strings.
        include_list = []
        for item in include:
            include_list.append(item.value)
        # Convert the list of strings to JSON.
        params['include'] = json.dumps(include_list)

    response = make_search_request(params)
    return parse_response_full(response)


def make_search_request(params: dict) -> dict:
    """Send a request to the Indicia taxa/searchAPI."""
    url = settings.indicia_url + 'taxa/search'
    params['taxon_list_id'] = settings.indicia_taxon_list_id

    try:
        r = requests.get(url, params=params,
                         auth=IndiciaAuth(settings.indicia_rest_password))
    except Exception as e:
        e.add_note("Indicia API connection error. Unable to "
                   "look up species information from Indicia.")
        raise
    else:
        if r.status_code == requests.codes.ok:
            return r.json()
        else:
            raise Exception("Indicia API error. " + r.json())


def parse_response_full(response: dict) -> IndiciaResponse:
    """Fit the full json response in to the IndiciaResponse model."""
    return IndiciaResponse(
        data=[IndiciaTaxon(**taxon) for taxon in response['data']
              ] if 'data' in response else None,
        count=response['count'] if 'count' in response else None,
        paging=response['paging'] if 'paging' in response else None,
        columns=response['columns'] if 'columns' in response else None
    )


def parse_response_taxa(response: dict) -> list[Taxon]:
    """Fit the taxon data in the response in to the Taxon model."""
    taxa = []
    if 'data' in response:
        for taxon in response['data']:
            taxa.append(Taxon(
                tvk=taxon['external_key'],
                preferred_tvk=taxon['external_key'],
                organism_key=taxon['organism_key'],
                name=taxon['taxon'],
                preferred_name=taxon['preferred_taxon']
            ))
    return taxa
