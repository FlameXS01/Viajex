from typing import List
from core.entities.diet import Diet
from core.repositories.diet_repository import DietRepository

class ListDietsPendingLiquidationUseCase:
    """Caso de uso para listar dietas pendientes de liquidación"""
    
    def __init__(self, diet_repository: DietRepository):
        self.diet_repository = diet_repository
    
    def execute(self) -> List[Diet]:
        return self.diet_repository.list_pending_liquidation()