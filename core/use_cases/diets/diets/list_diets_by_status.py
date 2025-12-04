from typing import List
from core.entities.diet import Diet, DietStatus
from core.repositories.diet_repository import DietRepository

class ListDietsByStatusUseCase:
    """Caso de uso para listar dietas por estado específico"""
    
    def __init__(self, diet_repository: DietRepository):
        self.diet_repository = diet_repository
    
    def execute(self, status: DietStatus) -> List[Diet]:
        return self.diet_repository.list_by_status(status) # type: ignore