from typing import Optional
from application.services.card_service import CardService
from application.dtos.cards_dtos import (
    CreateCardRequest, CreateCardResponse,
    GetCardRequest, GetCardResponse,
    UpdateCardRequest, UpdateCardResponse,
    DeleteCardRequest, DeleteCardResponse,
    ListCardsResponse
)

class CardController:
    def __init__(self, card_service: CardService):
        self.card_service = card_service

    def create_card(self, card_number: str, card_pin: str, amount: int) -> CreateCardResponse:
        # Crear card usando el servicio
        card = self.card_service.create_card(card_number, card_pin, amount)
        
        return CreateCardResponse(
            success=True,
            card_id=card.id,
            card_number=card.card_number,
            message="Card created successfully"
        )

    def get_card_by_id(self, card_id: int) -> GetCardResponse:
        card = self.card_service.get_card_by_id(card_id)
        
        if not card:
            return GetCardResponse(success=False, message="Card not found")
            
        return GetCardResponse(
            success=True,
            card=card,
            message="Card retrieved successfully"
        )

    def get_card_by_number(self, card_number: str) -> GetCardResponse:
        card = self.card_service.get_card_by_card_number(card_number)
        
        if not card:
            return GetCardResponse(success=False, message="Card not found")
            
        return GetCardResponse(
            success=True,
            card=card,
            message="Card retrieved successfully"
        )

    def update_card(self, card_id: int, card_number: str, card_pin: str) -> UpdateCardResponse:
        try:
            card = self.card_service.update_card(card_id, card_number, card_pin)
            return UpdateCardResponse(
                success=True,
                card=card,
                message="Card updated successfully"
            )
        except Exception as e:
            return UpdateCardResponse(success=False, message=str(e))

    def toggle_card_active(self, card_id: int) -> UpdateCardResponse:
        try:
            card = self.card_service.toggle_card_active(card_id)
            return UpdateCardResponse(
                success=True,
                card=card,
                message="Card status updated successfully"
            )
        except Exception as e:
            return UpdateCardResponse(success=False, message=str(e))

    def delete_card(self, card_id: int) -> DeleteCardResponse:
        success = self.card_service.delete_card(card_id)
        
        return DeleteCardResponse(
            success=success,
            message="Card deleted successfully" if success else "Failed to delete card"
        )

    def list_cards(self) -> ListCardsResponse:
        cards = self.card_service.get_all_cards()
        
        return ListCardsResponse(
            success=True,
            cards=cards,
            count=len(cards),
            message="Cards retrieved successfully"
        )