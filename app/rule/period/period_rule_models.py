from pydantic import BaseModel


class PeriodRuleResponse(BaseModel):
    tvk: str
    taxon: str
    start_date: str
    end_date: str


class PeriodRuleResponseTvk(BaseModel):
    organisation: str
    group: str
    start_date: str
    end_date: str
