from core.repositories.diet_repository import DietRepository
from core.repositories.diet_liquidation_repository import DietLiquidationRepository

class CardOnTheRoadUseCase:
    """Caso de uso para saber si una tarjeta todavia esta en una dieta"""
    
    def __init__(self, diet_repository: DietRepository):
        self.diet_repository = diet_repository
        
    
    def execute(self, card_id: int) -> bool:
        return self.diet_repository.card_on_the_road(card_id)