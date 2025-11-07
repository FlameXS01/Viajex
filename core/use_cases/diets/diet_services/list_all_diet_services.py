from typing import List
from core.entities.diet_service import DietService
from core.repositories.diet_service_repository import DietServiceRepository

class ListAllDietServicesUseCase:
    """Caso de uso para listar todos los servicios de dieta"""
    
    def __init__(self, diet_service_repository: DietServiceRepository):
        self.diet_service_repository = diet_service_repository
    
    def execute(self) -> List[DietService]:
        return self.diet_service_repository.list_all()