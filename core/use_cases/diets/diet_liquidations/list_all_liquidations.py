from typing import List, Optional
from core.entities.diet import Diet, DietStatus
from core.entities.diet_liquidation import DietLiquidation
from core.repositories.diet_liquidation_repository import DietLiquidationRepository

class ListAllLiquidationsUseCase:
    """Caso de uso para listar dietas por estado específico"""
    
    def __init__(self, diet_liquidation_repository: DietLiquidationRepository,):
        self.diet_liquidation_repository = diet_liquidation_repository
    
    def execute(self) -> Optional[list[DietLiquidation]]:
        return self.diet_liquidation_repository.list_all() 