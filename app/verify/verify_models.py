from typing import Optional, List
from pydantic import BaseModel, Field

from app.utility.sref import Sref


class Verify(BaseModel):
    id: int = Field(ge=1)
    name:  Optional[str] = None
    tvk: Optional[str] = None
    date: str
    sref: Sref
    stage: str | None = None


class OrgGroupRules(BaseModel):
    organisation: str
    group: str
    rules: Optional[List[str]] = None


class Verified(Verify):
    organism_key: Optional[str] = None
    preferred_tvk: Optional[str] = None
    id_difficulty: Optional[int] = None
    result: str = 'pass'
    messages: Optional[List[str]] = []


class VerifyPack(BaseModel):
    org_group_rules_list: Optional[List[OrgGroupRules]] = None
    records: List[Verify]


class VerifiedPack(BaseModel):
    org_group_rules_list: Optional[List[OrgGroupRules]] = None
    records: List[Verified]
    duration_ns: int
