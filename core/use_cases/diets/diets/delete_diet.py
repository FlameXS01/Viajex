from core.repositories.diet_repository import DietRepository
from core.repositories.diet_member_repository import DietMemberRepository
from core.repositories.diet_liquidation_repository import DietLiquidationRepository

class DeleteDietUseCase:
    """Caso de uso para eliminar una dieta"""
    
    def __init__(
        self,
        diet_repository: DietRepository,
        diet_member_repository: DietMemberRepository,
        diet_liquidation_repository: DietLiquidationRepository
    ):
        self.diet_repository = diet_repository
        self.diet_member_repository = diet_member_repository
        self.diet_liquidation_repository = diet_liquidation_repository
    
    def execute(self, diet_id: int) -> bool:
        # Verificar si existe liquidación asociada
        liquidation = self.diet_liquidation_repository.get_by_diet_id(diet_id)
        if liquidation:
            raise ValueError("No se puede eliminar una dieta que ya tiene liquidación")
        
        # Eliminar miembros de dieta grupal si existen
        self.diet_member_repository.delete_by_diet(diet_id)
        
        # Eliminar la dieta
        return self.diet_repository.delete(diet_id)