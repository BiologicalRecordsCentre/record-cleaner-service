from typing import Optional

from sqlmodel import Field, SQLModel


class System(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    key: str = Field(index=True)
    value: str


class Taxon(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tvk: str = Field(index=True)
    preferred_tvk: str = Field(index=True)
    organism_key: str
    name: str
    preferred_name: str
    rule_id: Optional[int]


class OrgGroup(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    organisation: str
    group: str


class Rule(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    org_group_id: int | None = Field(
        default=None, foreign_key='orggroup.id')
    tvk: str
    preferred_tvk: str = Field(index=True)
    name: str
    difficulty_rule_id: int | None = Field(
        default=None, foreign_key='difficultyrule.id')


class DifficultyRule(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    org_group_id: int | None = Field(
        default=None, foreign_key='orggroup.id')
    code: int
    text: str


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
