from sqlalchemy import select, update

from src.exceptions import DepthLimitExceededError
from src.models import Activity
from src.repositories.base import BaseRepository


class ActivityRepository(BaseRepository[Activity]):
    async def _get_depth(self, activity_id: int) -> int:
        """Рекурсивно находит глубину активности"""
        depth = 1
        current_id = activity_id

        while current_id:
            query = (
                select(Activity.parent_id)
                .where(
                    Activity.id == current_id,
                    Activity.is_deleted == False
                )
            )
            result = await self.db.execute(query)
            parent_id = result.scalar_one_or_none()

            if not parent_id:
                break

            depth += 1
            current_id = parent_id

        return depth

    async def create(self, obj_in: dict) -> Activity:
        """Создание activity с ограничением вложенности до 3 уровней"""
        parent_id = obj_in.get("parent_id")

        if parent_id:
            depth = await self._get_depth(parent_id)
            if depth >= 3:
                raise DepthLimitExceededError("Нельзя создать деятельность глубже 3 уровней")

        new_activity = Activity(**obj_in)
        self.db.add(new_activity)
        await self.db.commit()
        await self.db.refresh(new_activity)
        return new_activity

    async def soft_delete(self, activity_id: int):

        activity_cte = (
            select(Activity.id)
            .where(Activity.id == activity_id)
            .cte(name="activity_tree", recursive=True)
        )
        activity_cte = activity_cte.union_all(
            select(Activity.id)
            .where(Activity.parent_id == activity_cte.c.id)
        )

        # Обновляем все активности в дереве
        query_update = (
            update(Activity)
            .where(Activity.id.in_(select(activity_cte.c.id)))
            .values(is_deleted=True)
        )
        await self.db.execute(query_update)
        await self.db.commit()
