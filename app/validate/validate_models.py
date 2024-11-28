from typing import Optional, List
from pydantic import BaseModel, Field

from app.utility.sref import Sref


class Validate(BaseModel):
    id: int = Field(ge=1)
    name:  Optional[str] = None
    tvk: Optional[str] = None
    date: str
    sref: Sref
    vc: Optional[str | int] = None


class Validated(Validate):
    preferred_tvk: Optional[str] = None
    result: str = 'pass'
    messages: Optional[List[str]] = []
