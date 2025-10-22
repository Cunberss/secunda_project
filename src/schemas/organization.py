from typing import List

from pydantic import BaseModel, Field

from src.schemas.activity import ActivityBase


class OrganizationBase(BaseModel):
    id: int
    name: str = Field(..., description="Название организации")
    phones: list[str] = Field(default_factory=list, description="Список телефонов")
    building_id: int = Field(..., description="ID здания")
    activities: List[ActivityBase]

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": 'Рога и Копыта',
                "phones": [],
                "building_id": 1,
                "activities": [],
            }
        }