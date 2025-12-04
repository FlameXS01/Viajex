from typing import Optional
from core.entities.diet import Diet
from core.repositories.diet_repository import DietRepository

class GetAllUseCase:
    """Caso de uso para obtener todas las dietas"""
    
    def __init__(self, diet_repository: DietRepository):
        self.diet_repository = diet_repository
    
    def execute(self) -> list[Diet]:
        return self.diet_repository.get_all()