from typing import Optional

from sqlmodel import Field, SQLModel


class Taxon(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    external_key: str = Field(index=True)
    organism_key: str
    taxon: str
    preferred_taxon: str
    rule_id: Optional[int]


class Rule(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tvk: str
    name: str
    id_diff: int


class PeriodRule(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    rule_id: int
    start_day: Optional[int] = None
    start_month:  Optional[int] = None
    start_year:  Optional[int] = None
    end_day:  Optional[int] = None
    end_month:  Optional[int] = None
    end_year:  Optional[int] = None


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    hash: str
