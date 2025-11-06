from core.repositories.card_repository import CardRepository

class DeleteCardUseCase:
    def __init__(self, card_repository: CardRepository):
        self.card_repository = card_repository

    def execute(self, card_id: int) -> bool:
        # Verificar si la tarjeta existe
        card = self.card_repository.get_by_id(card_id)
        if not card:
            return False
        
        # Eliminar la tarjeta
        return self.card_repository.delete(card_id)