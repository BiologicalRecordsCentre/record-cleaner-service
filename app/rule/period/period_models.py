from pydantic import BaseModel


class PeriodRuleResponse(BaseModel):
    organism_key: str
    taxon: str
    start_date: str
    end_date: str


class PeriodRuleResponseOrganism(BaseModel):
    organisation: str
    group: str
    start_date: str
    end_date: str
