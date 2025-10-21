from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Building
from src.repositories.building_repo import BuildingRepository
from src.schemas.building import BuildingCreate, BuildingUpdate, BuildingList


class BuildingService:
    def __init__(self, session: AsyncSession):
        self.repo = BuildingRepository(session)

    async def list_buildings(self, skip: int = 0, limit: int = 100) -> BuildingList:
        """Получить список зданий с пагинацией"""
        items, total = await self.repo.get_all(skip=skip, limit=limit)
        return BuildingList(items=items, total=total)

    async def get_building(self, building_id: int) -> Optional[Building]:
        """Получить здание по ID"""
        return await self.repo.get_by_id(building_id)

    async def get_building_with_organizations(self, building_id: int) -> Optional[Building]:
        """Получить здание по ID с организациями"""
        return await self.repo.get_by_id_with_organizations(building_id)

    async def create_building(self, building_data: BuildingCreate) -> Building:
        """Создать новое здание"""
        # Проверяем, нет ли уже здания с такими координатами
        existing_building = await self.repo.get_by_coordinates(
            building_data.latitude,
            building_data.longitude
        )
        if existing_building:
            raise ValueError("Здание с такими координатами уже существует")

        return await self.repo.create(building_data)

    async def update_building(self, building_id: int, building_data: BuildingUpdate) -> Optional[Building]:
        """Обновить здание"""
        # Проверяем существование здания
        if not await self.repo.exists(building_id):
            return None

        return await self.repo.update(building_id, building_data)

    async def delete_building(self, building_id: int) -> bool:
        """Удалить здание"""
        return await self.repo.delete(building_id)

    async def search_buildings_by_address(self, query: str, skip: int = 0, limit: int = 50) -> BuildingList:
        """Поиск зданий по адресу"""
        if not query.strip():
            raise ValueError("Поисковый запрос не может быть пустым")

        items, total = await self.repo.search_by_address(
            address_query=query.strip(),
            skip=skip,
            limit=limit
        )
        return BuildingList(items=items, total=total)

    async def search_buildings_in_radius(
            self,
            latitude: float,
            longitude: float,
            radius_km: float
    ) -> List[Building]:
        """Поиск зданий в радиусе от точки"""
        if radius_km <= 0:
            raise ValueError("Радиус поиска должен быть положительным числом")

        return await self.repo.get_buildings_in_radius(
            latitude=latitude,
            longitude=longitude,
            radius_km=radius_km
        )

    async def search_buildings_in_bbox(
            self,
            min_lat: float,
            max_lat: float,
            min_lon: float,
            max_lon: float
    ) -> List[Building]:
        """Поиск зданий в bounding box"""
        if min_lat >= max_lat or min_lon >= max_lon:
            raise ValueError("Некорректные границы bounding box")

        return await self.repo.get_buildings_by_bbox(
            min_lat=min_lat,
            max_lat=max_lat,
            min_lon=min_lon,
            max_lon=max_lon
        )

    async def check_building_exists(self, building_id: int) -> bool:
        """Проверить существование здания"""
        return await self.repo.exists(building_id)

    async def validate_coordinates_unique(self, latitude: float, longitude: float,
                                          exclude_id: Optional[int] = None) -> bool:
        """Проверить уникальность координат"""
        existing = await self.repo.get_by_coordinates(latitude, longitude)
        if existing and existing.id != exclude_id:
            return False
        return True
