from src.repositories.organization_repo import OrganizationRepository


class OrganizationService:
    def __init__(self, repo: OrganizationRepository):
        self.repo = repo

    async def get_by_id(self, org_id: int):
        return await self.repo.get_by_id(org_id)

    async def list_by_building(self, building_id: int):
        return await self.repo.list_by_building(building_id)

    async def list_by_activity(self, activity_id: int):
        return await self.repo.list_by_activity(activity_id)

    async def list_in_radius(self, latitude: float, longitude: float, radius_km: float):
        return await self.repo.list_in_radius(latitude, longitude, radius_km)

    async def list_in_bbox(self, lat1: float, lon1: float, lat2: float, lon2: float):
        return await self.repo.list_in_bbox(lat1, lon1, lat2, lon2)

    async def search_by_name(self, query_text: str):
        return await self.repo.search_by_name(query_text)

    async def list_by_activity_tree(self, parent_activity_id: int):
        return await self.repo.list_by_activity_tree(parent_activity_id)
