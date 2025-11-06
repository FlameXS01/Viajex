from core.entities.cards import Card
from core.repositories.card_repository import CardRepository
from typing import Optional

class GetCardByNumberUseCase:
    def __init__(self, card_repository: CardRepository):
        self.card_repository = card_repository

    def execute(self, card_number: str) -> Optional[Card]:
        return self.card_repository.get_by_card_number(card_number)