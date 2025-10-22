from src.repositories.building_repo import BuildingRepository


class BuildingService:
    def __init__(self, repo: BuildingRepository):
        self.repo = repo

    async def list_in_bbox(self, lat1: float, lon1: float, lat2: float, lon2: float):
        return await self.repo.list_in_bbox(lat1, lon1, lat2, lon2)

    async def list_in_radius(self, latitude: float, longitude: float, radius_km: float):
        return await self.repo.list_in_radius(latitude, longitude, radius_km)

