from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.services.building_service import BuildingService


async def get_building_service(db: AsyncSession = Depends(get_session)) -> BuildingService:
    return BuildingService(db)
