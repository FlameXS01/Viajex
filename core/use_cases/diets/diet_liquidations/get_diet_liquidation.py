from typing import Optional
from core.entities.diet_liquidation import DietLiquidation
from core.repositories.diet_liquidation_repository import DietLiquidationRepository

class GetDietLiquidationUseCase:
    """Caso de uso para obtener una liquidación por ID"""
    
    def __init__(self, diet_liquidation_repository: DietLiquidationRepository):
        self.diet_liquidation_repository = diet_liquidation_repository
    
    def execute(self, liquidation_id: int) -> Optional[DietLiquidation]:
        return self.diet_liquidation_repository.get_by_id(liquidation_id)