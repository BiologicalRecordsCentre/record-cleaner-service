from pydantic import BaseModel


class DifficultyCodeResponse(BaseModel):
    difficulty: int
    text: str


class DifficultyRuleResponse(BaseModel):
    tvk: str
    taxon: str
    difficulty: int


class DifficultyRuleResponseTvk(BaseModel):
    organisation: str
    group: str
    difficulty: int
    text: str
