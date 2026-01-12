from core.entities.diet_liquidation import DietLiquidation
from core.repositories.diet_liquidation_repository import DietLiquidationRepository

class UpdateDietLiquidationUseCase:
    """Caso de uso para actualizar una liquidación existente"""
    
    def __init__(self, diet_liquidation_repository: DietLiquidationRepository):
        self.diet_liquidation_repository = diet_liquidation_repository
    
    def execute(self, liquidation_id: int, update_data: dict) -> DietLiquidation:
        liquidation = self.diet_liquidation_repository.get_by_id(liquidation_id)
        if not liquidation:
            raise ValueError("La liquidación no existe")
        
        # Actualizar campos permitidos
        for field, value in update_data.items():
            if hasattr(liquidation, field) and field not in ['id', 'diet_id', 'liquidation_number']:
                setattr(liquidation, field, value)
        
        return self.diet_liquidation_repository.update(liquidation)