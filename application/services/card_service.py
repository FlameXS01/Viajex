from core.entities.cards import Card
from core.repositories.card_repository import CardRepository
from core.use_cases.cards.create_card import CreateCardUseCase
from core.use_cases.cards.toggle_card_active import ToggleCardActiveUseCase
from core.use_cases.cards.update_card import UpdateCardUseCase
from core.use_cases.cards.delete_card import DeleteCardUseCase
from core.use_cases.cards.get_card_use_case import GetCardUseCase
from typing import Optional, List

class CardService:
        def __init__(
                self,
                card_repository: CardRepository,
                create_card_use_case: CreateCardUseCase,
                update_card_use_case: UpdateCardUseCase,
                toggle_card_active_use_case: ToggleCardActiveUseCase,
                delete_card_use_case: DeleteCardUseCase,
                get_card_use_case=GetCardUseCase
        ):
                self.card_repository = card_repository  # ✅ Instancia
                self.create_card_use_case = create_card_use_case
                self.update_card_use_case = update_card_use_case
                self.toggle_card_active_use_case = toggle_card_active_use_case
                self.delete_card_use_case = delete_card_use_case
        
        def create_card(self, card_number: str, card_pin: str, amount: int) -> Card:
                return self.create_card_use_case.execute(card_number, card_pin, amount)
        
        def get_card_by_id(self, card_id: int) -> Optional[Card]:
                return self.card_repository.get_by_id(card_id)
        
        def get_card_by_card_number(self, card_number: str) -> Optional[Card]:
                return self.card_repository.get_by_card_number(card_number)
        
        def get_all_cards(self) -> List[Card]:
                return self.card_repository.get_all()
        
        def toggle_card_active(self, card_id: int) -> Card:
                return self.toggle_card_active_use_case.execute(card_id)
        
        def update_card(self, card_id: int, card_number: str, card_pin: str) -> Card:
                return self.update_card_use_case.execute(card_id, card_number, card_pin)
        
        def delete_card(self, card_id: int) -> bool:
                return self.delete_card_use_case.execute(card_id)