from core.repositories.card_repository import CardRepository


class DeleteCardUseCase:
    """
    Caso de uso para eliminar una tarjeta del sistema
    """
    
    def __init__(self, card_repository: CardRepository):
        self.card_repository = card_repository

    def execute(self, card_id: int) -> bool:
        """
        Ejecuta la eliminación de una tarjeta
        
        Args:
            card_id: ID de la tarjeta a eliminar
            
        Returns:
            bool: True si fue eliminada, False si no existía
            
        Raises:
            ValueError: Si el card_id es inválido
        """
        # Validación básica
        if not card_id or card_id <= 0:
            raise ValueError("ID de tarjeta inválido")
        
        # Verificar existencia antes de eliminar (opcional)
        existing_card = self.card_repository.get_by_id(card_id)
        if not existing_card:
            return False
            
        # Ejecutar eliminación
        return self.card_repository.delete(card_id)