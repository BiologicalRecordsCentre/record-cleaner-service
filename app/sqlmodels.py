from typing import Optional

from sqlmodel import Field, SQLModel, UniqueConstraint, ForeignKey


class System(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    key: str = Field(index=True, unique=True)
    value: str


class Taxon(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tvk: str = Field(index=True, unique=True)
    preferred_tvk: str = Field(index=True)
    organism_key: str | None
    name: str
    preferred_name: str


class OrgGroup(SQLModel, table=True):
    __table_args__ = (UniqueConstraint('organisation', 'group'),)

    id: Optional[int] = Field(default=None, primary_key=True)
    organisation: str
    group: str
    commit: str | None = None
    additional_code_update: str | None = None
    additional_rule_update: str | None = None
    difficulty_code_update: str | None = None
    difficulty_rule_update: str | None = None
    period_rule_update: str | None = None
    tenkm_rule_update: str | None = None


class DifficultyCode(SQLModel, table=True):
    __table_args__ = (UniqueConstraint('org_group_id', 'code'),)

    id: Optional[int] = Field(default=None, primary_key=True)
    org_group_id: int = Field(foreign_key='orggroup.id', index=True)
    code: int
    text: str
    commit: str | None = None


class DifficultyRule(SQLModel, table=True):
    __table_args__ = (UniqueConstraint('org_group_id', 'taxon_id', 'stage'),)

    id: Optional[int] = Field(default=None, primary_key=True)
    org_group_id: int = Field(foreign_key='orggroup.id', index=True)
    taxon_id: int = Field(foreign_key='taxon.id', index=True)
    stage: str = Field(default='mature')
    difficulty_code_id: int = Field(
        foreign_key='difficultycode.id', index=True)
    commit: str | None = None


class AdditionalCode(SQLModel, table=True):
    __table_args__ = (UniqueConstraint('org_group_id', 'code'),)

    id: Optional[int] = Field(default=None, primary_key=True)
    org_group_id: int = Field(foreign_key='orggroup.id', index=True)
    code: int
    text: str
    commit: str | None = None


class AdditionalRule(SQLModel, table=True):
    __table_args__ = (UniqueConstraint('org_group_id', 'taxon_id', 'stage'),)

    id: Optional[int] = Field(default=None, primary_key=True)
    org_group_id: int = Field(foreign_key='orggroup.id', index=True)
    taxon_id: int = Field(foreign_key='taxon.id', index=True)
    stage: str = Field(default='mature')
    additional_code_id: int = Field(
        foreign_key='additionalcode.id', index=True)
    commit: str | None = None


class PeriodRule(SQLModel, table=True):
    __table_args__ = (UniqueConstraint('org_group_id', 'taxon_id'),)

    id: Optional[int] = Field(default=None, primary_key=True)
    org_group_id: int = Field(foreign_key='orggroup.id', index=True)
    taxon_id: int = Field(foreign_key='taxon.id', index=True)
    start_date:  str | None = None
    end_date:  str | None = None
    commit: str | None = None


class TenkmRule(SQLModel, table=True):
    __table_args__ = (UniqueConstraint('org_group_id', 'taxon_id', 'km100'),)

    id: Optional[int] = Field(default=None, primary_key=True)
    org_group_id: int = Field(foreign_key='orggroup.id', index=True)
    taxon_id: int = Field(foreign_key='taxon.id', index=True)
    km100:  str | None = None
    km10:  str | None = None
    coord_system:  str | None = None
    commit: str | None = None


class User(SQLModel, table=True):
    name: str = Field(primary_key=True)
    email: str
    hash: str
    is_admin: bool = Field(default=False)
    is_disabled: bool = Field(default=False)
