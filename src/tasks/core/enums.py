import enum


class UserRole(str, enum.Enum):
    student = "student"
    teacher = "teacher"
    manager = "manager"
    admin = "admin"


class TaskStatus(str, enum.Enum):
    new = "новая"
    in_progress = "в работе"
    submitted = "сдана"
    accepted = "принята"
