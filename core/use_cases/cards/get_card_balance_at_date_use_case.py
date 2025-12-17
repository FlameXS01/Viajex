from datetime import datetime
from core.repositories.card_transaction_repository import CardTransactionRepository
from core.repositories.card_repository import CardRepository


class GetCardBalanceAtDateUseCase:
    """
    Caso de uso para obtener el balance de una tarjeta en una fecha específica.
    """
    
    def __init__(
        self, 
        card_transaction_repository: CardTransactionRepository,
        card_repository: CardRepository
    ):
        self.card_transaction_repository = card_transaction_repository
        self.card_repository = card_repository
    
    def execute(self, card_id: int, target_date: datetime) -> float:
        """
        Obtiene el balance de una tarjeta en una fecha/hora específica.
        
        Args:
            card_id: ID de la tarjeta
            target_date: Fecha y hora para consultar el balance
            
        Returns:
            float: Balance en la fecha especificada
            
        Raises:
            ValueError: Si las validaciones fallan
        """
        # Validaciones
        if not card_id or card_id <= 0:
            raise ValueError("El ID de la tarjeta debe ser un número positivo")
        
        if not target_date:
            raise ValueError("La fecha objetivo es requerida")
        
        if target_date > datetime.now():
            raise ValueError("No se puede consultar balance en fecha futura")
        
        # Verificar que la tarjeta existe
        card = self.card_repository.get_by_id(card_id)
        if not card:
            raise ValueError(f"Tarjeta con ID {card_id} no encontrada")
        
        # Obtener balance histórico
        balance = self.card_transaction_repository.get_balance_at_date(card_id, target_date)
        
        return balance