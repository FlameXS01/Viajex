from typing import Optional
from core.entities.card import Card  # pyright: ignore[reportMissingImports] # ✅ Import corregido
from core.repositories.card_repository import CardRepository # pyright: ignore[reportMissingImports]

class GetCardUseCase:
    """
    Caso de uso para obtener una tarjeta por su ID
    """
    
    def __init__(self, card_repository: CardRepository):
        self.card_repository = card_repository

    def execute(self, card_id: int) -> Optional[Card]:
        """
        Obtiene una tarjeta por su ID
        
        Args:
            card_id: ID de la tarjeta a buscar
            
        Returns:
            Optional[Card]: La tarjeta encontrada o None si no existe
            
        Raises:
            ValueError: Si el card_id es inválido
        """
        # Validación básica del ID
        if not card_id or card_id <= 0:
            raise ValueError("ID de tarjeta inválido")
        
        return self.card_repository.get_by_id(card_id)