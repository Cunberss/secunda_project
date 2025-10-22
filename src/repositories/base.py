from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Generic, TypeVar, Type

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.db = session

    async def get_all(self):
        result = await self.db.execute(select(self.model))
        return result.scalars().all()

    async def get_by_id(self, obj_id: int):
        result = await self.db.execute(
            select(self.model).where(self.model.id == obj_id)
        )
        return result.scalar_one_or_none()

    async def create(self, obj_in: dict):
        obj = self.model(**obj_in)
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def update(self, db_obj, obj_in: dict):
        for key, value in obj_in.items():
            setattr(db_obj, key, value)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def delete(self, db_obj):
        await self.db.delete(db_obj)
        await self.db.commit()
