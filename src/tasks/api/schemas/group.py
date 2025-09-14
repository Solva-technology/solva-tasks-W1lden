from pydantic import BaseModel
from typing import List

class GroupCreateIn(BaseModel):
    name: str
    manager_id: int | None = None

class GroupOut(BaseModel):
    id: int
    name: str
    manager_id: int | None
    students: List[int]

    class Config:
        from_attributes = True
