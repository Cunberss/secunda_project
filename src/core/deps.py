from src.core.service_factory import get_service_factory
from src.models import Building, Organization
from src.repositories.building_repo import BuildingRepository
from src.repositories.organization_repo import OrganizationRepository
from src.services.building_service import BuildingService
from src.services.organization_service import OrganizationService

get_building_service = get_service_factory(BuildingRepository, Building, BuildingService)
get_organization_service = get_service_factory(OrganizationRepository, Organization, OrganizationService)
