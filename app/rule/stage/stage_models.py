from pydantic import BaseModel


class StageSynonymResponse(BaseModel):
    stage: str
    synonyms: str
