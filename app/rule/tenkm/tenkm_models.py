from pydantic import BaseModel


class TenkmRuleResponse(BaseModel):
    organism_key: str
    taxon: str
    km100: str
    km10: str
    coord_system: str


class TenkmRuleResponseOrganism(BaseModel):
    organisation: str
    group: str
    km100: str
    km10: str
    coord_system: str
