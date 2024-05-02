from typing import Optional, List
from pydantic import BaseModel, Field

from app.utility.sref import Sref


class Verify(BaseModel):
    id: int = Field(ge=1)
    date: str
    sref: Sref


class VerifyName(Verify):
    name: str


class VerifyTvk(Verify):
    tvk: str = Field(min_length=1)


class OrgGroupRules(BaseModel):
    organisation: str
    group: str
    rules: Optional[List[str]] = None


class Verified(Verify):
    name: Optional[str] = None
    tvk: Optional[str] = None
    ok: bool = True
    message: Optional[list] = []


class VerifyPackTvk(BaseModel):
    org_group_rules_list: Optional[List[OrgGroupRules]] = None
    records: List[VerifyTvk]


class VerifyPackName(BaseModel):
    org_group_rules_list: Optional[List[OrgGroupRules]] = None
    records: List[VerifyName]


class VerifiedPack(BaseModel):
    org_group_rules_list: Optional[List[OrgGroupRules]] = None
    records: List[Verified]
