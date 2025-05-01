from pydantic import BaseModel


class DifficultyCodeResponse(BaseModel):
    difficulty: int
    text: str


class DifficultyRuleResponse(BaseModel):
    organism_key: str
    taxon: str
    difficulty: int


class DifficultyRuleResponseOrganism(BaseModel):
    organisation: str
    group: str
    difficulty: int
    text: str
