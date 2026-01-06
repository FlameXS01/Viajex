from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from core.entities.enums import PaymentMethod

@dataclass
class DietLiquidation:
    """

    Entidad de dominio DietLiquidation que representa la liquidación
    de una dieta con las cantidades reales liquidadas.
    
    """
    diet_id: int
    liquidation_number: int
    liquidation_date: datetime
    breakfast_count_liquidated: int
    lunch_count_liquidated: int
    dinner_count_liquidated: int
    accommodation_count_liquidated: int
    accommodation_payment_method: PaymentMethod
    diet_service_id: int
    total_pay: Optional[float]
    id: Optional[int] = None
    accommodation_card_id: Optional[int] = None

    def __post_init__(self):
        """Validaciones después de la inicialización"""
        if self.liquidation_number < 1:
            raise ValueError("El número de liquidación debe ser mayor a 0")
        if any(count < 0 for count in [
            self.breakfast_count_liquidated,
            self.lunch_count_liquidated,
            self.dinner_count_liquidated,
            self.accommodation_count_liquidated
        ]):
            raise ValueError("Las cantidades liquidadas no pueden ser negativas")
        if self.accommodation_payment_method == PaymentMethod.CARD and not self.accommodation_card_id:
            raise ValueError("Se debe especificar una tarjeta cuando el pago es con tarjeta")