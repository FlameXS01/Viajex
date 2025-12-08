from core.repositories.card_repository import CardRepository

class DiscountCardUseCase:
    def __init__(self, card_repository: CardRepository):
        self.card_repository = card_repository

    def execute(self, card_id: int, amount: float) -> bool:
        # Verificar si la tarjeta existe
        card = self.card_repository.get_by_id(card_id)
        if not card:
            return False
        
        # Recargar la tarjeta
        return self.card_repository.discount(card_id, amount)