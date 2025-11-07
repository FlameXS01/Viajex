from typing import Optional
from core.entities.diet_liquidation import DietLiquidation
from core.repositories.diet_liquidation_repository import DietLiquidationRepository

class GetLiquidationByDietUseCase:
    """Caso de uso para obtener la liquidación asociada a una dieta"""
    
    def __init__(self, diet_liquidation_repository: DietLiquidationRepository):
        self.diet_liquidation_repository = diet_liquidation_repository
    
    def execute(self, diet_id: int) -> Optional[DietLiquidation]:
        return self.diet_liquidation_repository.get_by_diet_id(diet_id)