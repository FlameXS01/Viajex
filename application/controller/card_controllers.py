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

    def create_card(self, request: CreateCardRequest) -> CreateCardResponse:
        card = self.card_service.create_card(request.card_number, request.card_pin, request.amount)
        
        if not card:
            return CreateCardResponse(success=False, message="Failed to create card")
        
        return CreateCardResponse(
            success=True,
            card_id=card.id,
            card_number=card.card_number,
            amount=card.balance,  
            is_active=card.is_active,
            message="Card created successfully"
        )

    def get_card_by_id(self, request: GetCardRequest) -> GetCardResponse:
        card = self.card_service.get_card_by_id(request.card_id)
        
        if not card:
            return GetCardResponse(success=False, message="Card not found")
            
        return GetCardResponse(
            success=True,
            card_id=card.id,
            card_number=card.card_number,
            card_pin=card.card_pin,
            amount=card.balance,
            is_active=card.is_active,
            message="Card retrieved successfully"
        )

    def get_card_by_number(self, request: GetCardRequest) -> GetCardResponse:
        card = self.card_service.get_card_by_card_number(request.card_number)
        
        if not card:
            return GetCardResponse(success=False, message="Card not found")
            
        return GetCardResponse(
            success=True,
            card_id=card.id,
            card_number=card.card_number,
            card_pin=card.card_pin,
            amount=card.balance,
            is_active=card.is_active,
            message="Card retrieved successfully"
        )

    def update_card(self, request: UpdateCardRequest) -> UpdateCardResponse:
        try:
            card = self.card_service.update_card(
                card_id=request.card_id,
                card_number=request.card_number,
                card_pin=request.card_pin,
                amount=request.amount,
                is_active=request.is_active
            )
            
            if not card:
                return UpdateCardResponse(success=False, message="Card not found")
                
            return UpdateCardResponse(
                success=True,
                card_id=card.id,
                card_number=card.card_number,
                card_pin=card.card_pin,
                amount=card.balance,
                is_active=card.is_active,
                message="Card updated successfully"
            )
        except Exception as e:
            return UpdateCardResponse(success=False, message=str(e))

    def toggle_card_active(self, card_id: int) -> UpdateCardResponse:
        try:
            card = self.card_service.toggle_card_active(card_id)
            if not card:
                return UpdateCardResponse(success=False, message="Card not found")
                
            return UpdateCardResponse(
                success=True,
                card_id=card.id,
                card_number=card.card_number,
                card_pin=card.card_pin,
                amount=card.balance,
                is_active=card.is_active,
                message="Card status updated successfully"
            )
        except Exception as e:
            return UpdateCardResponse(success=False, message=str(e))

    def delete_card(self, request: DeleteCardRequest) -> DeleteCardResponse:
        success = self.card_service.delete_card(request.card_id)
        
        return DeleteCardResponse(
            success=success,
            message="Card deleted successfully" if success else "Failed to delete card"
        )

    def list_cards(self) -> ListCardsResponse:
        cards = self.card_service.get_all_cards()
        
        card_responses = [
            GetCardResponse(
                success=True,
                card_id=card.id,
                card_number=card.card_number,
                card_pin=card.card_pin,
                amount=card.balance,
                is_active=card.is_active,
                message=None
            ) for card in cards
        ]
        
        return ListCardsResponse(
            success=True,
            cards=card_responses,
            count=len(card_responses),
            message="Cards retrieved successfully"
        )