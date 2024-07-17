from typing import Optional, List
from pydantic import BaseModel, Field

from app.utility.sref import Sref


class Validate(BaseModel):
    id: int = Field(ge=1)
    date: str
    sref: Sref
    vc: Optional[str | int] = None


class ValidateName(Validate):
    name: str


class ValidateTvk(Validate):
    tvk: str = Field(min_length=1)


class Validated(Validate):
    name: Optional[str] = None
    tvk: Optional[str] = None
    id_difficulty: Optional[List[str]] = []
    ok: bool = True
    messages: Optional[List[str]] = []
