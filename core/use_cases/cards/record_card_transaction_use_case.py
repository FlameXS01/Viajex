from datetime import datetime
from typing import Optional
from core.entities.card_transaction import CardTransaction
from core.repositories.card_transaction_repository import CardTransactionRepository
from core.repositories.card_repository import CardRepository
import logging

logger = logging.getLogger(__name__)


class RecordCardTransactionUseCase:
    """
    Caso de uso para registrar una transacción de tarjeta.
    
    Responsabilidades:
    1. Validar la tarjeta existe y está activa
    2. Calcular balances antes/después
    3. Registrar transacción con auditoría completa
    4. Actualizar balance de la tarjeta
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
        transaction_type: str,
        amount: float,
        operation_date: Optional[datetime] = None,
        description: Optional[str] = None,
        reference_id: Optional[int] = None,
        reference_type: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> CardTransaction:
        """
        Ejecuta el registro de una transacción.
        
        Args:
            card_id: ID de la tarjeta
            transaction_type: Tipo de transacción (RECHARGE, DIET_ADVANCE, etc.)
            amount: Monto (positivo para créditos, negativo para débitos)
            operation_date: Fecha de la operación (default: ahora)
            description: Descripción opcional
            reference_id: ID de la entidad relacionada
            reference_type: Tipo de referencia
            user_id: ID del usuario que realiza la operación
            
        Returns:
            CardTransaction: La transacción registrada
            
        Raises:
            ValueError: Si las validaciones fallan
            Exception: Si hay error en el repositorio
        """
        # Validaciones básicas
        if not card_id or card_id <= 0:
            raise ValueError("El ID de la tarjeta debe ser un número positivo")
        
        if amount == 0:
            raise ValueError("El monto de la transacción no puede ser cero")
        
        # Obtener tarjeta
        card = self.card_repository.get_by_id(card_id)
        if not card:
            raise ValueError(f"Tarjeta con ID {card_id} no encontrada")
        
        # Validar saldo suficiente para débitos
        current_balance = float(str(card.balance)) if card.balance else float('0')
        if amount < 0 and abs(amount) > current_balance:
            raise ValueError(
                f"Saldo insuficiente. "
                f"Disponible: {current_balance:.2f}, "
                f"Requiere: {abs(amount):.2f}"
            )
        
        # Usar fecha actual si no se proporciona
        if operation_date is None:
            operation_date = datetime.now()
        
        # Calcular nuevo balance
        new_balance = current_balance + amount
        
        # Crear entidad de transacción
        transaction = CardTransaction(
            card_id=card_id,
            transaction_type=transaction_type,
            amount=amount,
            previous_balance=current_balance,
            new_balance=new_balance,
            operation_date=operation_date,
            notes=description  
        )
        
        # Asignar referencias si existen
        if reference_type == 'diet' and reference_id:
            transaction.diet_id = reference_id
        elif reference_type == 'liquidation' and reference_id:
            transaction.liquidation_id = reference_id
        
        # Guardar transacción
        saved_transaction = self.card_transaction_repository.save(transaction)
        
        # Actualizar balance de la tarjeta
        self.card_repository.update(card)
        
        logger.info(
            f"Transacción registrada exitosamente: "
            f"Tarjeta={card_id}, "
            f"Tipo={transaction_type}, "
            f"Monto={amount:.2f}, "
            f"Nuevo balance={new_balance:.2f}"
        )
        
        return saved_transaction