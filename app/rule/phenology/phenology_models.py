from pydantic import BaseModel


class PhenologyRuleResponse(BaseModel):
    organism_key: str
    taxon: str
    stage: str
    start_date: str
    end_date: str


class PhenologyRuleResponseOrganism(BaseModel):
    organisation: str
    group: str
    stage: str
    start_date: str
    end_date: str
