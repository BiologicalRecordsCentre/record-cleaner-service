from pydantic import BaseModel


class TenkmRuleResponse(BaseModel):
    tvk: str
    taxon: str
    km100: str
    km10: str
    coord_system: str


class TenkmRuleResponseTvk(BaseModel):
    organisation: str
    group: str
    km100: str
    km10: str
    coord_system: str
