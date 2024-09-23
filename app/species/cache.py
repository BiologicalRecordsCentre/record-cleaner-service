from functools import lru_cache

from fastapi import APIRouter, HTTPException, status
from sqlmodel import Session, func, select, delete

from app.database import DbDependency
from app.settings_env import EnvSettings
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
        tvk: str):
    return get_taxon_by_tvk(db, tvk)


@lru_cache(maxsize=1024)
def get_taxon_by_tvk(db: Session, env: EnvSettings, tvk: str) -> Taxon:
    """Look up the taxon with given TVK."""

    # First check our local database
    taxon = db.exec(
        select(Taxon)
        .where(Taxon.tvk == tvk)
    ).first()
    if not taxon:
        # If not found, add from the remote database.
        taxon = add_taxon_by_tvk(db, env, tvk)
    return taxon


def add_taxon_by_tvk(db: Session,  env: EnvSettings, tvk: str) -> Taxon:
    """Look up taxon with given TVK and add to cache."""
    params = {
        'search_code': tvk,
        'include': '["data"]'
    }
    response = driver.make_search_request(env, params)
    taxa = driver.parse_response_taxa(response)

    if len(taxa) == 0:
        raise ValueError(f"TVK {tvk} not recognised.")
    else:
        taxon = taxa[0]
        db.add(taxon)
        db.commit()
        db.refresh(taxon)
        return taxon


@lru_cache(maxsize=1024)
def get_taxon_by_name(db: Session, env: EnvSettings, name: str) -> Taxon:
    """Look up taxon with given name."""

    search_name = Search.get_search_name(name)
    # First check our local database.
    taxon = db.exec(
        select(Taxon).where(Taxon.search_name == search_name)
    ).first()
    if not taxon:
        # If not found, add from the remote database.
        taxon = add_taxon_by_name(db, env, name)
    return taxon


def add_taxon_by_name(db: Session, env: EnvSettings, name: str) -> Taxon:
    """Look up taxon and add to cache."""
    params = {
        'searchQuery': name,
        'include': '["data"]'
    }
    response = driver.make_search_request(env, params)
    taxa = driver.parse_response_taxa(response)

    if len(taxa) == 0:
        raise ValueError("Name not recognised.")
    else:
        taxon = taxa[0]
        db.add(taxon)
        db.commit()
        db.refresh(taxon)
        return taxon
