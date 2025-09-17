from typing import List

from pydantic import BaseModel


class GroupCreateIn(BaseModel):
    name: str
    manager_id: int | None = None
    teacher_id: int | None = None


class GroupOut(BaseModel):
    id: int
    name: str
    manager_id: int | None
    teacher_id: int | None
    students: List[int]

    class Config:
        from_attributes = True
