from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from core.entities.card_transaction import CardTransaction
from core.repositories.card_transaction_repository import CardTransactionRepository
from core.repositories.card_repository import CardRepository


class GetCardTransactionsUseCase:
    """
    Caso de uso para obtener transacciones de una tarjeta.
    
    Soporta filtrado por fecha, tipo de transacción y paginación.
    """
    
    def __init__(
        self, 
        card_transaction_repository: CardTransactionRepository,
        card_repository: CardRepository
    ):
        self.card_transaction_repository = card_transaction_repository
        self.card_repository = card_repository
    
    def execute(
        self,
        card_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        transaction_type: Optional[str] = None,
        page: int = 1,
        page_size: int = 50
    ) -> dict:
        """
        Obtiene transacciones de una tarjeta con paginación.
        
        Args:
            card_id: ID de la tarjeta
            start_date: Fecha inicial del filtro
            end_date: Fecha final del filtro
            transaction_type: Tipo de transacción a filtrar
            page: Número de página (comienza en 1)
            page_size: Elementos por página
            
        Returns:
            dict con transacciones y metadatos de paginación
            
        Raises:
            ValueError: Si las validaciones fallan
        """
        # Validaciones
        if not card_id or card_id <= 0:
            raise ValueError("El ID de la tarjeta debe ser un número positivo")
        
        if page < 1:
            raise ValueError("El número de página debe ser mayor o igual a 1")
        
        if page_size < 1 or page_size > 200:
            raise ValueError("El tamaño de página debe estar entre 1 y 200")
        
        # Verificar que la tarjeta existe
        card = self.card_repository.get_by_id(card_id)
        if not card:
            raise ValueError(f"Tarjeta con ID {card_id} no encontrada")
        
        # Calcular offset para paginación
        offset = (page - 1) * page_size
        
        # Obtener transacciones
        transactions = self.card_transaction_repository.get_by_card_id(
            card_id=card_id,
            start_date=start_date,
            end_date=end_date,
            transaction_type=transaction_type,
            limit=page_size,
            offset=offset
        )
        
        # Contar total de transacciones (para paginación)
        total_count = self.card_transaction_repository.count_by_card_id(
            card_id=card_id,
            start_date=start_date,
            end_date=end_date,
            transaction_type=transaction_type
        )
        
        # Calcular totales
        total_credits = Decimal('0')
        total_debits = Decimal('0')
        
        for transaction in transactions:
            if transaction.amount > 0:
                total_credits += transaction.amount
            else:
                total_debits += abs(transaction.amount)
        
        # Calcular metadatos de paginación
        total_pages = (total_count + page_size - 1) // page_size if page_size > 0 else 0
        
        return {
            'transactions': transactions,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total_count': total_count,
                'total_pages': total_pages,
                'has_next': page < total_pages,
                'has_previous': page > 1
            },
            'summary': {
                'total_credits': total_credits,
                'total_debits': total_debits,
                'net_movement': total_credits - total_debits
            }
        }