import datetime

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
    organism_key: str | None
    name: str
    preferred_name: str


class OrgGroup(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    organisation: str
    group: str
    difficulty_code_update: str | None = None
    difficulty_rule_update: str | None = None


class DifficultyRule(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    # The next 3 fields define a unique rule.
    org_group_id: int = Field(foreign_key='orggroup.id')
    taxon_id: int = Field(foreign_key="taxon.id")
    stage: str = Field(default='mature')
    ###
    difficulty_code_id: int = Field(foreign_key="difficultycode.id")
    commit: str | None = None


class DifficultyCodeBase(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)
    # The next 2 fields define a unique code.
    org_group_id: int = Field(foreign_key='orggroup.id')
    code: int
    ###
    text: str
    commit: str | None = None


class DifficultyCode(DifficultyCodeBase, table=True):
    pass


class AdditionalCode(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    # The next 2 fields define a unique code.
    org_group_id: int = Field(foreign_key='orggroup.id')
    code: int
    ###
    text: str
    commit: str | None = None


class PeriodRule(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    org_group_id: int = Field(foreign_key='orggroup.id')
    taxon_id: int = Field(foreign_key="taxon.id")
    start_day: int | None = None
    start_month:  int | None = None
    start_year:  int | None = None
    end_day:  int | None = None
    end_month:  int | None = None
    end_year:  int | None = None
    commit: str | None = None


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    hash: str
