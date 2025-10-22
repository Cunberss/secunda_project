from fastapi import APIRouter, Query, Path, Depends, HTTPException

from src.core.deps import get_organization_service
from src.schemas.organization import OrganizationBase
from src.services.organization_service import OrganizationService

router = APIRouter(prefix="/organizations", tags=["Организации"])


@router.get("/search", response_model=list[OrganizationBase])
async def search_by_name(
        query: str = Query(..., description="Часть названия организации"),
        service: OrganizationService = Depends(get_organization_service),
):
    """Поиск организаций по названию."""
    return await service.search_by_name(query)


@router.get("/nearby", response_model=list[OrganizationBase])
async def list_in_radius(
    latitude: float = Query(..., description="Широта центра"),
    longitude: float = Query(..., description="Долгота центра"),
    radius_km: float = Query(1.0, description="Радиус поиска в километрах"),
    service: OrganizationService = Depends(get_organization_service)
):
    """Список организаций в радиусе от точки."""
    return await service.list_in_radius(latitude, longitude, radius_km)


@router.get("/bbox", response_model=list[OrganizationBase])
async def list_in_bbox(
    lat1: float = Query(..., description="Минимальная широта (юго-запад)"),
    lon1: float = Query(..., description="Минимальная долгота (юго-запад)"),
    lat2: float = Query(..., description="Максимальная широта (северо-восток)"),
    lon2: float = Query(..., description="Максимальная долгота (северо-восток)"),
    service: OrganizationService = Depends(get_organization_service)
):
    """Список организаций в прямоугольной области."""
    return await service.list_in_bbox(lat1, lon1, lat2, lon2)


@router.get("/{org_id}", response_model=OrganizationBase)
async def get_organization(
        org_id: int = Path(..., description="ID организации"),
        service: OrganizationService = Depends(get_organization_service),
):
    """Вывод информации об организации по её идентификатору."""
    org = await service.get_by_id(org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Организация не найдена")
    return org


@router.get("/by_building/{building_id}", response_model=list[OrganizationBase])
async def list_by_building(
        building_id: int,
        service: OrganizationService = Depends(get_organization_service),
):
    """Список всех организаций, находящихся в конкретном здании."""
    return await service.list_by_building(building_id)


@router.get("/by_activity/{activity_id}", response_model=list[OrganizationBase])
async def list_by_activity(
        activity_id: int,
        service: OrganizationService = Depends(get_organization_service),
):
    """Список всех организаций, относящихся к указанному виду деятельности."""
    return await service.list_by_activity(activity_id)


@router.get("/by_activity_tree/{activity_id}", response_model=list[OrganizationBase])
async def list_by_activity_tree(
        activity_id: int,
        service: OrganizationService = Depends(get_organization_service),
):
    """
    Поиск по виду деятельности (включая все вложенные до 3 уровней).
    Например: Еда → Мясная продукция → Колбасы.
    """
    return await service.list_by_activity_tree(activity_id)

