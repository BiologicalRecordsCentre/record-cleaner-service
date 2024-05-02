from pydantic import BaseModel


class AdditionalCodeResponse(BaseModel):
    code: int
    text: str


class AdditionalRuleResponse(BaseModel):
    tvk: str
    taxon: str
    code: int


class AdditionalRuleResponseTvk(BaseModel):
    organisation: str
    group: str
    code: int
    text: str
