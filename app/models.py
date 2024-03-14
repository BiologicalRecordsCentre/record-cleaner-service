from typing import Optional

from sqlmodel import Field, SQLModel


class Taxon(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tvk: str = Field(index=True)
    preferred_tvk: str = Field(index=True)
    organism_key: str
    name: str
    preferred_name: str
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
