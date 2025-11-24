from core.repositories.diet_repository import DietRepository
from core.repositories.diet_liquidation_repository import DietLiquidationRepository

class DeleteDietUseCase:
    """Caso de uso para eliminar una dieta"""
    
    def __init__(
        self,
        diet_repository: DietRepository,
        diet_liquidation_repository: DietLiquidationRepository
    ):
        self.diet_repository = diet_repository
        self.diet_liquidation_repository = diet_liquidation_repository
    
    def execute(self, diet_id: int) -> bool:
        # Verificar si existe liquidación asociada
        liquidation = self.diet_liquidation_repository.get_by_diet_id(diet_id)
        if liquidation:
            raise ValueError("No se puede eliminar una dieta que ya tiene liquidación")
        
        # Eliminar la dieta
        return self.diet_repository.delete(diet_id)