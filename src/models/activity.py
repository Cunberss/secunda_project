from sqlalchemy import String, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core import Base
from src.models.mixins import BaseModelMixin


class Activity(Base, BaseModelMixin):
    __tablename__ = "activities"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True, nullable=False, index=True)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("activities.id", ondelete="SET NULL"), nullable=True)

    # Самоссылка
    parent: Mapped["Activity | None"] = relationship(
        "Activity", remote_side="Activity.id", back_populates="children"
    )
    children: Mapped[list["Activity"]] = relationship(
        "Activity", back_populates="parent", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_activity_parent_id", "parent_id"),
    )

    def __repr__(self):
        return f"<Activity(id={self.id}, name='{self.name}', parent_id={self.parent_id})>"
