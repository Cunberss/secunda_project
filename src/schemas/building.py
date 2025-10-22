from typing import List

from pydantic import BaseModel, Field, field_validator

from src.schemas.organization import OrganizationBase


class BuildingBase(BaseModel):
    id: int = Field(..., description="ID здания")
    address: str = Field(..., min_length=1, max_length=500, description="Адрес здания")
    latitude: float = Field(..., ge=-90, le=90, description="Широта от -90 до 90")
    longitude: float = Field(..., ge=-180, le=180, description="Долгота от -180 до 180")
    organizations: List[OrganizationBase]

    @field_validator("address")
    def validate_address(cls, v):
        if not v.strip():
            raise ValueError("Адрес не может быть пустым")
        return v.strip()

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "address": "г. Москва, ул. Ленина 1",
                "latitude": 55.7558,
                "longitude": 37.6176,
                "organizations": [],
            }
        }