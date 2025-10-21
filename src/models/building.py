from sqlalchemy import String, Float, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from geoalchemy2 import Geometry
from src.core.database import Base


class Building(Base):
    __tablename__ = "buildings"

    id: Mapped[int] = mapped_column(primary_key=True)
    address: Mapped[str] = mapped_column(String(500), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)

    # Геометрия точки (для поиска в радиусе)
    geom: Mapped[str] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326), nullable=False
    )

    # Отношение один-ко-многим с организациями
    organizations = relationship(
        "Organization", back_populates="building", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_building_geom", "geom", postgresql_using="gist"),
        Index("idx_building_coords", "latitude", "longitude"),
    )

    def __repr__(self):
        return f"<Building(id={self.id}, address='{self.address}')>"
