from datetime import datetime
from pydantic import BaseModel
from tasks.core.enums import TaskStatus

class TaskCreateIn(BaseModel):
    title: str
    description: str | None = None
    student_id: int
    group_id: int
    deadline: datetime | None = None

class TaskOut(BaseModel):
    id: int
    title: str
    description: str | None
    status: TaskStatus
    student_id: int
    group_id: int
    deadline: datetime | None

    class Config:
        from_attributes = True

class TaskPatchIn(BaseModel):
    title: str | None = None
    description: str | None = None
    status: TaskStatus | None = None
    deadline: datetime | None = None
