from pydantic import BaseModel, Field, field_validator
from typing import Optional


class BuildingBase(BaseModel):
    address: str = Field(..., min_length=1, max_length=500, description="Адрес здания")
    latitude: float = Field(..., ge=-90, le=90, description="Широта от -90 до 90")
    longitude: float = Field(..., ge=-180, le=180, description="Долгота от -180 до 180")

    @field_validator("address")
    def validate_address(cls, v):
        if not v.strip():
            raise ValueError("Адрес не может быть пустым")
        return v.strip()


class BuildingCreate(BuildingBase):
    """Схема для создания нового здания."""
    pass


class BuildingUpdate(BaseModel):
    """Схема для обновления существующего здания."""
    address: Optional[str] = Field(None, min_length=1, max_length=500)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)

    @field_validator("address")
    def validate_address(cls, v):
        if v is not None and not v.strip():
            raise ValueError("Адрес не может быть пустым")
        return v.strip() if v else v


class BuildingOut(BuildingBase):
    id: int = Field(..., description="ID здания")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "address": "г. Москва, ул. Ленина 1",
                "latitude": 55.7558,
                "longitude": 37.6176,
            }
        }


class BuildingList(BaseModel):
    items: list[BuildingOut]
    total: int

    class Config:
        json_schema_extra = {
            "example": {
                "items": [
                    {
                        "id": 1,
                        "address": "г. Москва, ул. Ленина 1",
                        "latitude": 55.7558,
                        "longitude": 37.6176,
                    },
                    {
                        "id": 2,
                        "address": "г. Екатеринбург, ул. Мира 10",
                        "latitude": 56.8389,
                        "longitude": 60.6057,
                    },
                ],
                "total": 2,
            }
        }
