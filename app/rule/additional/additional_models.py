from pydantic import BaseModel


class AdditionalCodeResponse(BaseModel):
    code: int
    text: str


class AdditionalRuleResponse(BaseModel):
    organism_key: str
    taxon: str
    code: int


class AdditionalRuleResponseOrganism(BaseModel):
    organisation: str
    group: str
    code: int
    text: str
