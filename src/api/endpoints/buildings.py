from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from src.core.deps import get_building_service
from src.services.building_service import BuildingService
from src.schemas.building import BuildingCreate, BuildingUpdate, BuildingOut, BuildingList

router = APIRouter(prefix="/buildings", tags=["buildings"])


@router.get("/", response_model=BuildingList, summary="Получить список зданий")
async def get_buildings(
    skip: int = Query(0, ge=0, description="Количество записей для пропуска"),
    limit: int = Query(100, ge=1, le=1000, description="Лимит записей"),
    service: BuildingService = Depends(get_building_service),
):
    """Получить список всех зданий с пагинацией"""
    return await service.list_buildings(skip=skip, limit=limit)


@router.get("/{building_id}", response_model=BuildingOut, summary="Получить здание по ID")
async def get_building(
    building_id: int,
    service: BuildingService = Depends(get_building_service),
):
    """Получить информацию о конкретном здании"""
    building = await service.get_building(building_id)
    if not building:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Здание не найдено"
        )
    return building


@router.get("/{building_id}/with-organizations", response_model=BuildingOut, summary="Получить здание с организациями")
async def get_building_with_organizations(
    building_id: int,
    service: BuildingService = Depends(get_building_service),
):
    """Получить информацию о здании вместе с организациями"""
    building = await service.get_building_with_organizations(building_id)
    if not building:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Здание не найдено"
        )
    return building


@router.post("/", response_model=BuildingOut, status_code=status.HTTP_201_CREATED, summary="Создать новое здание")
async def create_building(
    building_data: BuildingCreate,
    service: BuildingService = Depends(get_building_service),
):
    """Создать новое здание"""
    try:
        return await service.create_building(building_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{building_id}", response_model=BuildingOut, summary="Обновить здание")
async def update_building(
    building_id: int,
    building_data: BuildingUpdate,
    service: BuildingService = Depends(get_building_service),
):
    """Обновить информацию о здании"""
    updated_building = await service.update_building(building_id, building_data)
    if not updated_building:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Здание не найдено"
        )
    return updated_building


@router.delete("/{building_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Удалить здание")
async def delete_building(
    building_id: int,
    service: BuildingService = Depends(get_building_service),
):
    """Удалить здание"""
    if not await service.delete_building(building_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Здание не найдено"
        )


@router.get("/search/address", response_model=BuildingList, summary="Поиск зданий по адресу")
async def search_buildings_by_address(
    query: str = Query(..., min_length=1, max_length=100, description="Поисковый запрос по адресу"),
    skip: int = Query(0, ge=0, description="Количество записей для пропуска"),
    limit: int = Query(50, ge=1, le=200, description="Лимит записей"),
    service: BuildingService = Depends(get_building_service),
):
    """Поиск зданий по адресу"""
    try:
        return await service.search_buildings_by_address(query, skip, limit)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/search/radius", response_model=List[BuildingOut], summary="Поиск зданий в радиусе")
async def search_buildings_in_radius(
    latitude: float = Query(..., ge=-90, le=90, description="Широта центра поиска"),
    longitude: float = Query(..., ge=-180, le=180, description="Долгота центра поиска"),
    radius_km: float = Query(..., ge=0.1, le=100, description="Радиус поиска в километрах"),
    service: BuildingService = Depends(get_building_service),
):
    """Найти все здания в указанном радиусе от точки"""
    try:
        return await service.search_buildings_in_radius(latitude, longitude, radius_km)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/search/bbox", response_model=List[BuildingOut], summary="Поиск зданий в bounding box")
async def search_buildings_in_bbox(
    min_lat: float = Query(..., ge=-90, le=90, description="Минимальная широта"),
    max_lat: float = Query(..., ge=-90, le=90, description="Максимальная широта"),
    min_lon: float = Query(..., ge=-180, le=180, description="Минимальная долгота"),
    max_lon: float = Query(..., ge=-180, le=180, description="Максимальная долгота"),
    service: BuildingService = Depends(get_building_service),
):
    """Найти все здания в bounding box"""
    try:
        return await service.search_buildings_in_bbox(min_lat, max_lat, min_lon, max_lon)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )