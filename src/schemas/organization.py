from pydantic import BaseModel, Field


class OrganizationBase(BaseModel):
    name: str = Field(..., description="Название организации")
    phones: list[str] = Field(default_factory=list, description="Список телефонов")
    building_id: int = Field(..., description="ID здания")


class OrganizationOut(OrganizationBase):
    id: int

    class Config:
        from_attributes = True
