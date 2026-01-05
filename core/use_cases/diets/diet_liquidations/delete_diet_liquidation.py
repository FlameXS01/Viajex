from core.repositories.diet_liquidation_repository import DietLiquidationRepository
from core.repositories.diet_repository import DietRepository
from core.entities.diet import DietStatus

class DeleteDietLiquidationUseCase:
    """Caso de uso para eliminar una liquidación"""
    
    def __init__(
        self,
        diet_liquidation_repository: DietLiquidationRepository,
        diet_repository: DietRepository
    ):
        self.diet_liquidation_repository = diet_liquidation_repository
        self.diet_repository = diet_repository
    
    def execute(self, liquidation_id: int) -> bool:
        liquidation = self.diet_liquidation_repository.get_by_id(liquidation_id)
        if not liquidation:
            raise ValueError("La liquidación no existe")
        
        # Obtener la dieta asociada y cambiar su estado a REQUESTED
        diet = self.diet_repository.get_by_id(liquidation.diet_id)
        if diet:
            status = DietStatus.REQUESTED.value
            self.diet_repository.update_status(liquidation.diet_id, status)
        
        # Eliminar la liquidación
        return self.diet_liquidation_repository.delete(liquidation_id)