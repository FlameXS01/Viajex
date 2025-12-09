from typing import List
from core.entities.cards import Card
from core.repositories.card_repository import CardRepository

class GetAviableCardsUseCase:
    def __init__(self, card_repository: CardRepository):
        self.card_repository = card_repository

    def execute(self) -> List[Card]:
        return self.card_repository.get_aviable()