from functools import lru_cache

from fastapi import APIRouter, HTTPException, status
from sqlmodel import SQLModel, Session, func, select, delete, or_

from app.auth import Auth
from app.database import DB
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
    session: DB
):
    count = session.exec(
        select(func.count(Taxon.id))
    ).first()
    return {"count": count}


@router.get(
    "/cache/{id}",
    tags=['Species Cache'],
    summary="Get item from species cache.",
    response_model=Taxon)
async def read_cache_item(
        session: DB,
        id: int):
    taxon = session.get(Taxon, id)
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
    session: DB
):
    session.exec(
        delete(Taxon)
    )
    session.commit()
    return {"ok": True}


@router.delete(
    "/cache/{id}",
    tags=['Species Cache'],
    summary="Delete item from species cache.",
    response_model=dict)
async def delete_cache_item(
        session: DB,
        id: int):
    session.exec(
        delete(Taxon).where(Taxon.id == id)
    )
    session.commit()
    return {"ok": True}


@router.get(
    "/cache/taxon_by_tvk/{tvk}",
    tags=['Species Cache'],
    summary="Get taxon with given TVK from cache.",
    response_model=Taxon)
async def read_taxon_by_tvk(
        session: DB,
        tvk: str):
    return get_taxon_by_tvk(session, tvk)


@lru_cache(maxsize=1024)
def get_taxon_by_tvk(session: Session, tvk: str) -> Taxon:
    """Look up the taxon with given TVK."""

    # First check our local database
    taxon = session.exec(
        select(Taxon)
        .where(Taxon.tvk == tvk)
    ).first()
    if not taxon:
        # If not found, add from the remote database.
        taxon = add_taxon_by_tvk(session, tvk)
    return taxon


def add_taxon_by_tvk(session: Session, tvk: str) -> Taxon:
    """Look up taxon with given TVK and add to cache."""
    params = {
        'search_code': tvk,
        'include': '["data"]'
    }
    response = driver.make_search_request(params)
    taxa = driver.parse_response_taxa(response)

    if len(taxa) == 0:
        raise ValueError("TVK not recognised.")
    else:
        taxon = taxa[0]
        session.add(taxon)
        session.commit()
        session.refresh(taxon)
        return taxon


@lru_cache(maxsize=1024)
def get_taxon_by_name(session: Session, name: str) -> Taxon:
    """Look up taxon with given name."""

    search_name = Search.get_search_name(name)
    # First check our local database.
    taxon = session.exec(
        select(Taxon).where(Taxon.search_name == search_name)
    ).first()
    if not taxon:
        # If not found, add from the remote database.
        taxon = add_taxon_by_name(session, name)
    return taxon


def add_taxon_by_name(session: Session, name: str) -> Taxon:
    """Look up taxon and add to cache."""
    params = {
        'searchQuery': name,
        'include': '["data"]'
    }
    response = driver.make_search_request(params)
    taxa = driver.parse_response_taxa(response)

    if len(taxa) == 0:
        raise ValueError("Name not recognised.")
    else:
        taxon = taxa[0]
        session.add(taxon)
        session.commit()
        session.refresh(taxon)
        return taxon
