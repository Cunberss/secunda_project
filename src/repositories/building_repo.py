# src/repositories/building_repository.py
from typing import List, Optional, Tuple
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.models.building import Building
from src.schemas.building import BuildingCreate, BuildingUpdate


class BuildingRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, building_id: int) -> Optional[Building]:
        """Получить здание по ID"""
        result = await self.db.execute(
            select(Building).where(Building.id == building_id)
        )
        return result.scalar_one_or_none()

    async def get_by_id_with_organizations(self, building_id: int) -> Optional[Building]:
        """Получить здание по ID с загрузкой организаций"""
        result = await self.db.execute(
            select(Building)
            .where(Building.id == building_id)
            .options(selectinload(Building.organizations))
        )
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> Tuple[List[Building], int]:
        """Получить все здания с пагинацией"""
        # Получаем общее количество
        count_result = await self.db.execute(select(func.count(Building.id)))
        total = count_result.scalar_one()

        # Получаем данные с пагинацией
        buildings_result = await self.db.execute(
            select(Building)
            .offset(skip)
            .limit(limit)
            .order_by(Building.id)
        )
        buildings = buildings_result.scalars().all()

        return list(buildings), total

    async def create(self, building_data: BuildingCreate) -> Building:
        """Создать новое здание"""
        # Создаем WKT (Well-Known Text) для геометрии
        wkt_point = f"POINT({building_data.longitude} {building_data.latitude})"

        db_building = Building(
            address=building_data.address,
            latitude=building_data.latitude,
            longitude=building_data.longitude,
            geom=wkt_point
        )

        self.db.add(db_building)
        await self.db.commit()
        await self.db.refresh(db_building)
        return db_building

    async def update(self, building_id: int, building_data: BuildingUpdate) -> Optional[Building]:
        """Обновить здание"""
        db_building = await self.get_by_id(building_id)
        if not db_building:
            return None

        update_data = building_data.model_dump(exclude_unset=True)

        # Если обновляются координаты, обновляем геометрию
        if 'latitude' in update_data or 'longitude' in update_data:
            lat = update_data.get('latitude', db_building.latitude)
            lon = update_data.get('longitude', db_building.longitude)
            update_data['geom'] = f"POINT({lon} {lat})"

        for field, value in update_data.items():
            setattr(db_building, field, value)

        await self.db.commit()
        await self.db.refresh(db_building)
        return db_building

    async def delete(self, building_id: int) -> bool:
        """Удалить здание"""
        db_building = await self.get_by_id(building_id)
        if not db_building:
            return False

        await self.db.delete(db_building)
        await self.db.commit()
        return True

    async def get_by_coordinates(self, latitude: float, longitude: float, tolerance: float = 0.0001) -> Optional[
        Building]:
        """Найти здание по координатам с допуском"""
        result = await self.db.execute(
            select(Building).where(
                (func.abs(Building.latitude - latitude) <= tolerance) &
                (func.abs(Building.longitude - longitude) <= tolerance)
            )
        )
        return result.scalar_one_or_none()

    async def search_by_address(self, address_query: str, skip: int = 0, limit: int = 50) -> Tuple[List[Building], int]:
        """Поиск зданий по адресу"""
        # Получаем общее количество для пагинации
        count_result = await self.db.execute(
            select(func.count(Building.id)).where(
                Building.address.ilike(f"%{address_query}%")
            )
        )
        total = count_result.scalar_one()

        # Получаем данные
        buildings_result = await self.db.execute(
            select(Building)
            .where(Building.address.ilike(f"%{address_query}%"))
            .offset(skip)
            .limit(limit)
            .order_by(Building.id)
        )
        buildings = buildings_result.scalars().all()

        return list(buildings), total

    async def get_buildings_in_radius(self, latitude: float, longitude: float, radius_km: float) -> List[Building]:
        """Найти здания в радиусе от точки (в километрах)"""
        # Используем PostGIS функцию ST_DWithin для поиска в радиусе
        point_wkt = f"POINT({longitude} {latitude})"

        result = await self.db.execute(
            select(Building).where(
                func.ST_DWithin(
                    Building.geom,
                    func.ST_GeomFromText(point_wkt, 4326),
                    radius_km * 1000  # Конвертируем км в метры
                )
            ).order_by(
                func.ST_Distance(
                    Building.geom,
                    func.ST_GeomFromText(point_wkt, 4326)
                )
            )
        )

        return list(result.scalars().all())

    async def get_buildings_by_bbox(self, min_lat: float, max_lat: float, min_lon: float, max_lon: float) -> List[
        Building]:
        """Найти здания в bounding box"""
        result = await self.db.execute(
            select(Building).where(
                (Building.latitude >= min_lat) &
                (Building.latitude <= max_lat) &
                (Building.longitude >= min_lon) &
                (Building.longitude <= max_lon)
            ).order_by(Building.id)
        )
        return list(result.scalars().all())

    async def exists(self, building_id: int) -> bool:
        """Проверить существование здания"""
        result = await self.db.execute(
            select(func.count(Building.id)).where(Building.id == building_id)
        )
        return result.scalar_one() > 0