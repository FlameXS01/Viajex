from core.repositories.diet_repository import DietRepository
from core.repositories.diet_liquidation_repository import DietLiquidationRepository

class ResetCountersUseCase:
    """Caso de uso para reiniciar los números secuenciales"""
    
    def __init__(
        self,
        diet_repository: DietRepository,
        diet_liquidation_repository: DietLiquidationRepository
    ):
        self.diet_repository = diet_repository
        self.diet_liquidation_repository = diet_liquidation_repository
    
    def execute(self) -> bool:
        """Reinicia ambos contadores (anticipos y liquidaciones)"""
        success_advance = self.diet_repository.reset_advance_numbers()
        success_liquidation = self.diet_liquidation_repository.reset_liquidation_numbers()
        
        return success_advance and success_liquidation