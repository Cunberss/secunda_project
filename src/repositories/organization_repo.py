from geoalchemy2 import WKTElement
from sqlalchemy import select, func
from shapely.geometry import box
from sqlalchemy.orm import selectinload

from src.models import Organization, org_activity, Building, Activity
from src.repositories.base import BaseRepository


class OrganizationRepository(BaseRepository[Organization]):

    async def list_by_building(self, building_id: int):
        query = select(Organization).where(Organization.building_id == building_id).options(selectinload(Organization.activities))
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_by_id(self, obj_id: int):
        query = select(Organization).where(Organization.id == obj_id).options(selectinload(Organization.activities))
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_by_activity(self, activity_id: int):
        query = (
            select(Organization)
            .join(org_activity)
            .where(org_activity.c.activity_id == activity_id).options(selectinload(Organization.activities))
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def list_in_radius(self, latitude: float, longitude: float, radius_km: float):
        query = (
            select(Organization)
            .join(Organization.building)
            .join(Organization.activities)
            .where(
                func.ST_DistanceSphere(
                    Building.geom,
                    func.ST_MakePoint(longitude, latitude)
                ) <= radius_km * 1000
            )
            .options(
                selectinload(Organization.activities)
            )
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def list_in_bbox(self, lat1: float, lon1: float, lat2: float, lon2: float):
        shapely_box = box(lon1, lat1, lon2, lat2)
        bbox_geom = WKTElement(shapely_box.wkt, srid=4326)

        query = (
            select(Organization)
            .join(Organization.building)
            .join(Organization.activities)
            .where(func.ST_Intersects(Building.geom, bbox_geom))
            .options(
                selectinload(Organization.activities)
            )
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def search_by_name(self, query_text: str):
        query = select(Organization).where(
            func.lower(Organization.name).like(f"%{query_text.lower()}%")).options(selectinload(Organization.activities)
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def list_by_activity_tree(self, parent_activity_id: int):
        activity_cte = (
            select(Activity.id, Activity.parent_id)
            .where(Activity.id == parent_activity_id)
            .cte(name="activity_tree", recursive=True)
        )
        activity_cte = activity_cte.union_all(
            select(Activity.id, Activity.parent_id)
            .where(Activity.parent_id == activity_cte.c.id)
        )

        query = (
            select(Organization)
            .join(org_activity)
            .where(org_activity.c.activity_id.in_(select(activity_cte.c.id)))
            .options(selectinload(Organization.activities))  # ← вот это важно
        )
        result = await self.db.execute(query)
        return result.scalars().all()
