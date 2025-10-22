from fastapi import APIRouter
from src.api.endpoints import buildings, organizations

api_router = APIRouter()

api_router.include_router(buildings.router)
api_router.include_router(organizations.router)
