from geoalchemy2 import WKTElement
from sqlalchemy import select, func
from shapely.geometry import box
from src.models import Organization, org_activity, Building, Activity
from src.repositories.base import BaseRepository


class OrganizationRepository(BaseRepository[Organization]):
    async def list_by_building(self, building_id: int):
        query = select(Organization).where(Organization.building_id == building_id)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def list_by_activity(self, activity_id: int):
        query = (
            select(Organization)
            .join(org_activity)
            .where(org_activity.c.activity_id == activity_id)
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def list_in_radius(self, latitude: float, longitude: float, radius_km: float):
        query = (
            select(Organization)
            .join(Building)
            .where(
                func.ST_DistanceSphere(
                    Building.geom,
                    func.ST_MakePoint(longitude, latitude)
                ) <= radius_km * 1000
            )
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def list_in_bbox(self, lat1: float, lon1: float, lat2: float, lon2: float):
        shapely_box = box(lon1, lat1, lon2, lat2)
        bbox_geom = WKTElement(shapely_box.wkt, srid=4326)

        query = (
            select(Organization)
            .join(Building)
            .where(func.ST_Intersects(Building.geom, bbox_geom))
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def search_by_name(self, query_text: str):
        query = select(Organization).where(
            func.lower(Organization.name).like(f"%{query_text.lower()}%")
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
        )
        result = await self.db.execute(query)
        return result.scalars().all()
