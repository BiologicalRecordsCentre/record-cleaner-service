from pydantic import BaseModel


class OrgGroupResponse(BaseModel):
    id: int
    organisation: str
    group: str
