from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class CardTransaction:
    """
    Entidad que representa una transacción de tarjeta.
    
    Cada transacción registra:
    - Un movimiento (crédito o débito)
    - Los balances antes y después
    - Metadatos para trazabilidad
    """
    id: Optional[int] = None
    card_id: int = None
    transaction_type: str = None
    amount: float = None
    previous_balance: float = None
    new_balance: float = None
    operation_date: datetime = None
    recorded_at: Optional[datetime] = None
    diet_id: Optional[int] = None
    liquidation_id: Optional[int] = None
    notes: Optional[str] = None

    @property
    def is_credit(self) -> bool:
        """Determina si la transacción es un crédito (entrada de dinero)"""
        return self.amount > 0 if self.amount is not None else False

    @property
    def is_debit(self) -> bool:
        """Determina si la transacción es un débito (salida de dinero)"""
        return self.amount < 0 if self.amount is not None else False

    def __post_init__(self):
        """Validaciones después de la inicialización"""
        if self.amount is None:
            raise ValueError("El monto de la transacción es requerido")
        
        if self.previous_balance is None:
            raise ValueError("El saldo anterior es requerido")
            
        if self.new_balance is None:
            raise ValueError("El nuevo saldo es requerido")
            
        # Validar consistencia de balances
        expected_new_balance = self.previous_balance + self.amount
        if round(self.new_balance, 2) != round(expected_new_balance, 2):
            raise ValueError(
                f"Inconsistencia en balances: "
                f"{self.previous_balance} + {self.amount} = {expected_new_balance}, "
                f"pero new_balance es {self.new_balance}"
            )