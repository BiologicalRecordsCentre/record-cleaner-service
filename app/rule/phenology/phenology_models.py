from pydantic import BaseModel


class PhenologyRuleResponse(BaseModel):
    tvk: str
    taxon: str
    stage: str
    start_date: str
    end_date: str


class PhenologyRuleResponseTvk(BaseModel):
    organisation: str
    group: str
    stage: str
    start_date: str
    end_date: str
