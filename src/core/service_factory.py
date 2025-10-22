from typing import Type, Callable
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session


def get_service_factory(
        repo_class: Type,
        model_class: Type,
        service_class: Type
) -> Callable[[AsyncSession], object]:
    async def _get_service(db: AsyncSession = Depends(get_session)):
        repo = repo_class(model_class, db)
        return service_class(repo)

    return _get_service
