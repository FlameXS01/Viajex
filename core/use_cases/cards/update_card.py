from typing import Optional
from core.entities.cards import Card
from core.repositories.card_repository import CardRepository

class UpdateCardUseCase:
    def __init__(self, card_repository: CardRepository):
        self.card_repository = card_repository

    def execute(self, card_id: int, card_number: str, description: str, amount: float, is_active: bool) -> Optional[Card]:
        # Validar que el número de tarjeta tenga entre 12 y 16 dígitos
        if len(card_number) < 12 or len(card_number) > 16 or not card_number.isdigit():
            raise ValueError("El número de tarjeta debe tener entre 12 y 16 dígitos")
        
        # Validar que el monto sea positivo
        if amount < 0:
            raise ValueError("El monto no puede ser negativo")
        
        # Obtener la tarjeta existente
        existing_card = self.card_repository.get_by_id(card_id)
        if not existing_card:
            raise ValueError("Tarjeta no encontrada")
        
        # Verificar si el nuevo número de tarjeta ya existe (excluyendo la tarjeta actual)
        other_card = self.card_repository.get_by_card_number(card_number)
        if other_card and other_card.id != card_id:
            raise ValueError("Ya existe otra tarjeta con este número")
        
        # Actualizar los datos
        existing_card.card_number = card_number
        existing_card.description = description
        existing_card.amount = amount
        existing_card.is_active = is_active
        
        # Guardar los cambios
        return self.card_repository.save(existing_card)