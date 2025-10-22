from pydantic import BaseModel, Field, field_validator
from typing import Optional, List


class ActivityBase(BaseModel):
    id: int
    name: str = Field(..., min_length=1, max_length=200, description="Название деятельности")
    parent_id: Optional[int] = Field(None, description="ID родительской деятельности (если есть)")

    @field_validator("name")
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError("Название не может быть пустым")
        return v.strip()

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Образование",
                "parent_id": None,
            }
        }


class ActivityDetails(ActivityBase):
    id: int
    children: List["ActivityDetails"] = []

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Образование",
                "parent_id": None,
                "children": [
                    {"id": 2, "name": "Школы", "parent_id": 1, "children": []}
                ]
            }
        }
