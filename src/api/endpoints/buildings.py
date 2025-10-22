from typing import List
from fastapi import APIRouter, Depends, Query

from src.core.deps import get_building_service
from src.schemas.building import BuildingBase
from src.services.building_service import BuildingService

router = APIRouter(prefix="/buildings", tags=["Здания"])


@router.get("/bbox", response_model=List[BuildingBase], summary="Поиск зданий в bounding box")
async def search_buildings_in_bbox(
        lat1: float = Query(..., description="Минимальная широта (юго-запад)"),
        lon1: float = Query(..., description="Минимальная долгота (юго-запад)"),
        lat2: float = Query(..., description="Максимальная широта (северо-восток)"),
        lon2: float = Query(..., description="Максимальная долгота (северо-восток)"),
        service: BuildingService = Depends(get_building_service)
):
    return await service.list_in_bbox(lat1, lon1, lat2, lon2)


@router.get("/nearby", response_model=list[BuildingBase], summary="Поиск зданий в заданном радиусе")
async def list_in_radius(
        latitude: float = Query(..., description="Широта центра"),
        longitude: float = Query(..., description="Долгота центра"),
        radius_km: float = Query(1.0, description="Радиус поиска в километрах"),
        service: BuildingService = Depends(get_building_service)
):
    """Список организаций в радиусе от точки."""
    return await service.list_in_radius(latitude, longitude, radius_km)
