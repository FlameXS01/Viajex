from typing import Optional
from core.entities.diet import Diet
from core.repositories.diet_repository import DietRepository

class GetDietUseCase:
    """Caso de uso para obtener una dieta por ID"""
    
    def __init__(self, diet_repository: DietRepository):
        self.diet_repository = diet_repository
    
    def execute(self, diet_id: int) -> Optional[Diet]:
        return self.diet_repository.get_by_id(diet_id)