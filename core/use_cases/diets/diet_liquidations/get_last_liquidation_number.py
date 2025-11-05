from core.repositories.diet_liquidation_repository import DietLiquidationRepository

class GetLastLiquidationNumberUseCase:
    """Caso de uso para obtener el último número de liquidación utilizado"""
    
    def __init__(self, diet_liquidation_repository: DietLiquidationRepository):
        self.diet_liquidation_repository = diet_liquidation_repository
    
    def execute(self) -> int:
        return self.diet_liquidation_repository.get_last_liquidation_number()