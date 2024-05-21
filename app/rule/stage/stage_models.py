from pydantic import BaseModel


class StageSynonymResponse(BaseModel):
    stage: str
    text: str
