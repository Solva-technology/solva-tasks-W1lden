from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from tasks.core.db import Base

groups_students = Table(
    "groups_students",
    Base.metadata,
    Column(
        "group_id",
        ForeignKey("groups.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    ),
)


class Group(Base):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    manager_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    teacher_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    students: Mapped[list["User"]] = relationship(
        back_populates="groups", secondary=groups_students, lazy="selectin"
    )
    manager: Mapped["User | None"] = relationship(
        back_populates="managed_groups",
        foreign_keys=[manager_id],
        lazy="selectin",
    )
    teacher: Mapped["User | None"] = relationship(
        back_populates="teaching_groups",
        foreign_keys=[teacher_id],
        lazy="selectin",
    )
    tasks: Mapped[list["Task"]] = relationship(
        back_populates="group", cascade="all,delete-orphan", lazy="selectin"
    )
