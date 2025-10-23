from geoalchemy2 import WKTElement
from shapely.geometry import box
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload, with_loader_criteria

from src.models import Organization, org_activity, Building, Activity
from src.repositories.base import BaseRepository


class OrganizationRepository(BaseRepository[Organization]):
    """Репозиторий для работы с организациями (Organization)"""

    async def list_by_building(self, building_id: int):
        query = (
            select(Organization)
            .where(
                Organization.building_id == building_id,
                Organization.is_deleted == False
            )
            .options(
                selectinload(Organization.activities),
                with_loader_criteria(
                    Activity,
                    Activity.is_deleted == False
                )
            )
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_by_id(self, obj_id: int):
        query = (
            select(Organization)
            .where(
                Organization.id == obj_id,
                Organization.is_deleted == False
            )
            .options(
                selectinload(Organization.activities),
                with_loader_criteria(
                    Activity,
                    Activity.is_deleted == False
                )
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_by_activity(self, activity_id: int):
        query = (
            select(Organization)
            .join(org_activity)
            .join(Activity)
            .where(
                org_activity.c.activity_id == activity_id,
                Organization.is_deleted == False,
                Activity.is_deleted == False
            )
            .options(
                selectinload(Organization.activities),
                with_loader_criteria(
                    Activity,
                    Activity.is_deleted == False
                )
            )
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
                ) <= radius_km * 1000,
                Organization.is_deleted == False,
                Building.is_deleted == False,
                Activity.is_deleted == False
            )
            .options(
                selectinload(Organization.activities),
                with_loader_criteria(
                    Activity,
                    Activity.is_deleted == False
                )
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
            .where(
                func.ST_Intersects(Building.geom, bbox_geom),
                Organization.is_deleted == False,
                Building.is_deleted == False,
                Activity.is_deleted == False
            )
            .options(
                selectinload(Organization.activities),
                with_loader_criteria(
                    Activity,
                    Activity.is_deleted == False
                )
            )
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def search_by_name(self, query_text: str):
        query = (
            select(Organization)
            .where(
                func.lower(Organization.name).like(f"%{query_text.lower()}%"),
                Organization.is_deleted == False
            )
            .options(
                selectinload(Organization.activities),
                with_loader_criteria(
                    Activity,
                    Activity.is_deleted == False
                )
            )
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def list_by_activity_tree(self, parent_activity_id: int):
        """
        Возвращает все организации, связанные с активностями в дереве (включая потомков).
        """
        activity_cte = (
            select(Activity.id, Activity.parent_id)
            .where(
                Activity.id == parent_activity_id,
                Activity.is_deleted == False
            )
            .cte(name="activity_tree", recursive=True)
        )

        activity_cte = activity_cte.union_all(
            select(Activity.id, Activity.parent_id)
            .where(
                Activity.parent_id == activity_cte.c.id,
                Activity.is_deleted == False
            )
        )

        query = (
            select(Organization)
            .join(org_activity)
            .join(Activity)
            .where(
                org_activity.c.activity_id.in_(select(activity_cte.c.id)),
                Organization.is_deleted == False,
                Activity.is_deleted == False
            )
            .options(
                selectinload(Organization.activities),
                with_loader_criteria(
                    Activity,
                    Activity.is_deleted == False
                )
            )
        )
        result = await self.db.execute(query)
        return result.scalars().all()
