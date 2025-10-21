from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.building_repo import BuildingRepository
from src.schemas.building import BuildingCreate, BuildingUpdate


class BuildingService:
    def __init__(self, session: AsyncSession):
        self.repo = BuildingRepository(session)

    async def list_buildings(self):
        return await self.repo.get_all()

    async def get_building(self, building_id: int):
        return await self.repo.get_by_id(building_id)

    async def create_building(self, building_data: BuildingCreate):
        data = building_data.model_dump()
        return await self.repo.create(data)

    async def update_building(self, building_id: int, building_data: BuildingUpdate):
        obj = await self.repo.get_by_id(building_id)
        if not obj:
            return None
        return await self.repo.update(obj, building_data.model_dump(exclude_unset=True))

    async def delete_building(self, building_id: int):
        obj = await self.repo.get_by_id(building_id)
        if not obj:
            return None
        await self.repo.delete(obj)
        return True
