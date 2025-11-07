from core.repositories.diet_liquidation_repository import DietLiquidationRepository

class ResetLiquidationNumbersUseCase:
    """Caso de uso específico para reiniciar números de liquidación"""
    
    def __init__(self, diet_liquidation_repository: DietLiquidationRepository):
        self.diet_liquidation_repository = diet_liquidation_repository
    
    def execute(self) -> bool:
        return self.diet_liquidation_repository.reset_liquidation_numbers()