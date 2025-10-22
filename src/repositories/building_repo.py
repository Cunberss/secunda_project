from geoalchemy2 import WKTElement
from shapely.geometry import box
from sqlalchemy import func, select
from sqlalchemy.orm import contains_eager

from src.models import Building, Organization
from src.repositories.base import BaseRepository


class BuildingRepository(BaseRepository[Building]):

    async def list_in_bbox(self, lat1: float, lon1: float, lat2: float, lon2: float):
        shapely_box = box(lon1, lat1, lon2, lat2)
        bbox_geom = WKTElement(shapely_box.wkt, srid=4326)

        query = (
            select(Building)
            .join(Building.organizations)
            .join(Organization.activities)
            .where(func.ST_Intersects(Building.geom, bbox_geom))
            .options(
                contains_eager(Building.organizations)
                .contains_eager(Organization.activities)
            )
        )
        result = await self.db.execute(query)
        return result.unique().scalars().all()

    async def list_in_radius(self, latitude: float, longitude: float, radius_km: float):
        query = (
            select(Building)
            .join(Building.organizations)
            .join(Organization.activities)
            .where(
                func.ST_DistanceSphere(
                    Building.geom,
                    func.ST_MakePoint(longitude, latitude)
                ) <= radius_km * 1000
            )
            .options(
                contains_eager(Building.organizations)
                .contains_eager(Organization.activities)
            )
        )
        result = await self.db.execute(query)
        return result.unique().scalars().all()
