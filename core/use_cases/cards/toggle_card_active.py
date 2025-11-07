from typing import Optional
from core.entities.cards import Card
from core.repositories.card_repository import CardRepository

class ToggleCardActiveUseCase:
    def __init__(self, card_repository: CardRepository):
        self.card_repository = card_repository

    def execute(self, card_id: int) -> Optional[Card]:
        card = self.card_repository.get_by_id(card_id)
        if not card:
            return None
        
        # Cambiar el estado activo/inactivo
        card.is_active = not card.is_active
        
        # Guardar el cambio
        return self.card_repository.save(card)