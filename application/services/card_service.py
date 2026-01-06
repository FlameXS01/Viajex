from typing import List, Optional
from core.entities.cards import Card
from core.use_cases.cards.aviable_card import GetAviableCardsUseCase
from core.use_cases.cards.create_card import CreateCardUseCase
from core.use_cases.cards.delete_card import DeleteCardUseCase
from core.use_cases.cards.discount_card import DiscountCardUseCase
from core.use_cases.cards.update_card import UpdateCardUseCase
from core.use_cases.cards.get_card_use_case import GetCardByIdUseCase
from core.use_cases.cards.get_all_cards import GetAllCardsUseCase
from core.use_cases.cards.toggle_card_active import ToggleCardActiveUseCase
from core.use_cases.cards.get_card_by_number import GetCardByNumberUseCase  
from core.use_cases.cards.recharged_card import RechargeCardUseCase  

class CardService:
    def __init__(self, 
                 create_card_use_case: CreateCardUseCase,
                 delete_card_use_case: DeleteCardUseCase,
                 update_card_use_case: UpdateCardUseCase,
                 get_card_by_id_use_case: GetCardByIdUseCase,
                 get_all_cards_use_case: GetAllCardsUseCase,
                 get_aviable_cards_use_case: GetAviableCardsUseCase,
                 toggle_card_active_use_case: ToggleCardActiveUseCase,
                 recharge_card_use_case: RechargeCardUseCase,
                 get_card_by_number_use_case: GetCardByNumberUseCase,
                 discount_card_use_case: DiscountCardUseCase):  
        self.create_card_use_case = create_card_use_case
        self.delete_card_use_case = delete_card_use_case
        self.update_card_use_case = update_card_use_case
        self.get_card_by_id_use_case = get_card_by_id_use_case
        self.get_all_cards_use_case = get_all_cards_use_case
        self.toggle_card_active_use_case = toggle_card_active_use_case
        self.get_card_by_number_use_case = get_card_by_number_use_case  
        self.recharge_card_use_case = recharge_card_use_case
        self.discount_card_use_case = discount_card_use_case
        self.get_aviable_cards_use_case = get_aviable_cards_use_case

    def create_card(self, card_number: str, card_pin: str, amount: float) -> Optional[Card]:
        return self.create_card_use_case.execute(card_number, card_pin, amount)
    
    def delete_card(self, card_id: int) -> bool:
        return self.delete_card_use_case.execute(card_id)
    
    def recharge_card(self, card_id: int, amount: float, is_refound) -> bool:
        return self.recharge_card_use_case.execute(card_id, amount, is_refound)
    
    def discount_card(self, card_id: int, amount: float) -> bool:
        return self.discount_card_use_case.execute(card_id, amount)
    
    def update_card(self, card_id: int, card_number: str, card_pin: str) -> Optional[Card]:
        return self.update_card_use_case.execute(card_id, card_number, card_pin)

    def get_card_by_id(self, card_id: int) -> Optional[Card]:
        return self.get_card_by_id_use_case.execute(card_id)

    def get_card_by_card_number(self, card_number: str) -> Optional[Card]:
        return self.get_card_by_number_use_case.execute(card_number)

    def get_all_cards(self) -> List[Card]:
        return self.get_all_cards_use_case.execute()
    
    def get_aviable_cards(self) -> List[Card]:
        return self.get_aviable_cards_use_case.execute()

    def toggle_card_active(self, card_id: int) -> Optional[Card]:
        return self.toggle_card_active_use_case.execute(card_id)
    