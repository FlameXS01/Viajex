from dataclasses import dataclass
from datetime import date



@dataclass
class CardBalanceSnapshot:
    """
    Entidad que representa un snapshot diario del balance de una tarjeta.
    
    Optimiza consultas históricas y reportes al precalcular
    resúmenes diarios.
    """
    id: int = None
    card_id: int = None
    snapshot_date: date = None
    opening_balance: float = None
    closing_balance: float = None
    total_credits: float = None
    total_debits: float = None
    transaction_count: int = None

    @property
    def net_movement(self) -> float:
        """Movimiento neto del día (créditos - débitos)"""
        return self.total_credits - self.total_debits if self.total_credits and self.total_debits else float('0')

    @property
    def expected_closing_balance(self) -> float:
        """Balance de cierre esperado basado en cálculos"""
        if self.opening_balance is not None and self.total_credits is not None and self.total_debits is not None:
            return self.opening_balance + self.total_credits - self.total_debits
        return float('0')

    def __post_init__(self):
        """Validaciones después de la inicialización"""
        if self.card_id is None:
            raise ValueError("El ID de la tarjeta es requerido")
            
        if self.snapshot_date is None:
            raise ValueError("La fecha del snapshot es requerida")
            
        # Validar que los totales sean no negativos
        if self.total_credits is not None and self.total_credits < 0:
            raise ValueError("Los créditos totales no pueden ser negativos")
            
        if self.total_debits is not None and self.total_debits < 0:
            raise ValueError("Los débitos totales no pueden ser negativos")
            
        if self.transaction_count is not None and self.transaction_count < 0:
            raise ValueError("El conteo de transacciones no puede ser negativo")