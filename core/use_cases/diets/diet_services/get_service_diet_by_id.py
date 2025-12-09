from typing import Optional
from core.entities.diet_service import DietService
from core.repositories.diet_service_repository import DietServiceRepository

class GetDietServiceByIdUseCase:
    """Caso de uso para obtener el servicio de dieta por id"""
    
    def __init__(self, diet_service_repository: DietServiceRepository):
        self.diet_service_repository = diet_service_repository
    
    def execute(self, id: int) -> Optional[DietService]:
        return self.diet_service_repository.get_by_id(id)