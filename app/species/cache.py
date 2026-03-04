from cachetools import cached, LRUCache
from cachetools.keys import hashkey

from fastapi import APIRouter, HTTPException, status
from sqlmodel import Session, func, select, delete

from app.database import DbDependency
from app.settings_env import EnvDependency, EnvSettings
from app.sqlmodels import Taxon
import app.species.indicia as driver
from app.utility.search import Search

router = APIRouter()


@router.get(
    "/cache/count",
    tags=['Species Cache'],
    summary="Get number of records in species cache.",
    response_model=dict)
async def read_cache_size(
    db: DbDependency
):
    count = db.exec(
        select(func.count(Taxon.id))
    ).first()
    return {"count": count}


@router.get(
    "/cache/{id}",
    tags=['Species Cache'],
    summary="Get item from species cache.",
    response_model=Taxon)
async def read_cache_item(
        db: DbDependency,
        id: int):
    taxon = db.get(Taxon, id)
    if not taxon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No item found with ID {id}.")

    return taxon


@router.delete(
    "/cache/all",
    tags=['Species Cache'],
    summary="Empty the species cache.",
    response_model=dict)
async def cache_clear(
    db: DbDependency
):
    db.exec(
        delete(Taxon)
    )
    db.commit()
    return {"ok": True}


@router.delete(
    "/cache/{id}",
    tags=['Species Cache'],
    summary="Delete item from species cache.",
    response_model=dict)
async def delete_cache_item(
        db: DbDependency,
        id: int):
    db.exec(
        delete(Taxon).where(Taxon.id == id)
    )
    db.commit()
    return {"ok": True}


@router.get(
    "/cache/taxon_by_tvk/{tvk}",
    tags=['Species Cache'],
    summary="Get taxon with given TVK from cache.",
    response_model=Taxon)
async def read_taxon_by_tvk(
        db: DbDependency,
        env: EnvDependency,
        tvk: str):
    # This endpoint is different from /species/taxon_by_tvk as it returns
    # additional information, including the cache id.
    try:
        return get_taxon_by_tvk(db, env, tvk)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e))


def get_taxon_by_tvk(db: Session, env: EnvSettings, tvk: str) -> Taxon:
    """Look up the taxon with given TVK.

    Wrapper for _get_taxon_by_tvk_wrapped so that exceptions can be cached.
    """

    taxon = _get_taxon_by_tvk_wrapped(db, env, tvk)
    if isinstance(taxon, Exception):
        raise taxon
    else:
        return taxon


@cached(cache=LRUCache(maxsize=1024), key=lambda db, env, tvk: hashkey(tvk))
def _get_taxon_by_tvk_wrapped(db: Session, env: EnvSettings, tvk: str) -> Taxon:
    """Look up the taxon with given TVK."""

    # First check our local database
    taxon = db.exec(
        select(Taxon)
        .where(Taxon.tvk == tvk)
    ).first()
    if not taxon:
        # If not found, add from the remote database.
        taxon = _add_taxon_by_tvk(db, env, tvk)
    return taxon


def _add_taxon_by_tvk(db: Session,  env: EnvSettings, tvk: str) -> Taxon:
    """Look up taxon with given TVK and add to cache.

    Exceptions are returned so that they can be cached.
     """
    params = {
        'search_code': tvk,
        'include': '["data"]'
    }
    response = driver.make_search_request(env, params)
    taxa = driver.parse_response_taxa(response)

    if len(taxa) == 0:
        return ValueError(f"TVK {tvk} not recognised.")
    else:
        taxon = taxa[0]
        db.add(taxon)
        db.commit()
        db.refresh(taxon)
        return taxon


def get_taxon_by_name(db: Session, env: EnvSettings, name: str) -> Taxon:
    """Look up taxon with given name.

    Wrapper for _get_taxon_by_name_wrapped so that exceptions can be cached.
    """

    taxon = _get_taxon_by_name_wrapped(db, env, name)
    if isinstance(taxon, Exception):
        raise taxon
    else:
        return taxon


@cached(cache=LRUCache(maxsize=1024), key=lambda db, env, name: hashkey(name))
def _get_taxon_by_name_wrapped(db: Session, env: EnvSettings, name: str) -> Taxon:
    """Look up taxon with given name in local database."""

    search_name = Search.get_search_name(name)
    # First check our local database.
    taxon = db.exec(
        select(Taxon).where(Taxon.search_name == search_name)
    ).first()
    if not taxon:
        # If not found, add from the remote database.
        taxon = _add_taxon_by_name(db, env, name)
    return taxon


def _add_taxon_by_name(db: Session, env: EnvSettings, name: str) -> Taxon:
    """Look up taxon in remote database and add to local.

    Exceptions are returned so that they can be cached.
    """
    params = {
        'searchQuery': name,
        'include': '["data"]',
        'wholeWords': 'true',
    }
    response = driver.make_search_request(env, params)
    taxa = driver.parse_response_taxa(response)

    if len(taxa) == 0:
        return ValueError(f"Name '{name}' not recognised.")
    else:
        # Use the first suggestion. This may be naive but Indicia does seem to
        # sort the results in a helpful way.
        taxon = taxa[0]
        # The name returned is not always the same as the one supplied.
        # E.g. A search for 'Tern' returns 'Tern species'.
        request_search_name = Search.get_search_name(name)
        response_search_name = Search.get_search_name(taxon.name)
        if request_search_name != response_search_name:
            error = f"Name '{name}' not recognised. "
            suggestions = ', '.join(taxon.name for taxon in taxa)
            error += f"Suggestions: {suggestions}"
            return ValueError(error)

        # Add the new taxon to the cache.
        db.add(taxon)
        db.commit()
        db.refresh(taxon)
        return taxon
