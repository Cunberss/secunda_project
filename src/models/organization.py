from sqlalchemy import String, ForeignKey, Index, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB
from src.core import Base
from src.models.mixins import BaseModelMixin

# Ассоциативная таблица организация-деятельность
org_activity = Table(
    "org_activity",
    Base.metadata,
    Column("organization_id", ForeignKey("organizations.id", ondelete="CASCADE"), primary_key=True),
    Column("activity_id", ForeignKey("activities.id", ondelete="CASCADE"), primary_key=True),
)


class Organization(Base, BaseModelMixin):
    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(300), nullable=False, index=True)
    phones: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    building_id: Mapped[int] = mapped_column(ForeignKey("buildings.id", ondelete="CASCADE"), nullable=False)

    # Связи
    building = relationship("Building", back_populates="organizations")
    activities = relationship("Activity", secondary=org_activity, backref="organizations")

    __table_args__ = (
        Index("idx_organization_building_id", "building_id"),
    )

    def __repr__(self):
        return f"<Organization(id={self.id}, name='{self.name}')>"
