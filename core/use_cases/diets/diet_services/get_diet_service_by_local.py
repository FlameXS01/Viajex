from typing import Optional
from core.entities.diet_service import DietService
from core.repositories.diet_service_repository import DietServiceRepository

class GetDietServiceByLocalUseCase:
    """Caso de uso para obtener el servicio de dieta por localidad"""
    
    def __init__(self, diet_service_repository: DietServiceRepository):
        self.diet_service_repository = diet_service_repository
    
    def execute(self, is_local: bool) -> Optional[DietService]:
        return self.diet_service_repository.get_by_local(is_local)