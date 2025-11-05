from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional
from core.entities.enums import DietStatus, PaymentMethod

@dataclass
class Diet:
    """

    Entidad de dominio Diet que representa un anticipo de dieta
    con todos los servicios y cantidades planeadas.
    
    """
    is_local: bool
    start_date: date
    end_date: date
    description: str
    advance_number: int
    is_group: bool
    status: DietStatus
    request_user_id: int
    diet_service_id: int
    breakfast_count: int
    lunch_count: int
    dinner_count: int
    accommodation_count: int
    accommodation_payment_method: PaymentMethod
    created_at: datetime
    id: Optional[int] = None
    accommodation_card_id: Optional[int] = None

    def __post_init__(self):
        """Validaciones después de la inicialización"""
        if self.start_date > self.end_date:
            raise ValueError("La fecha de inicio no puede ser posterior a la fecha fin")
        if self.advance_number < 1:
            raise ValueError("El número de anticipo debe ser mayor a 0")
        if any(count < 0 for count in [
            self.breakfast_count, 
            self.lunch_count, 
            self.dinner_count, 
            self.accommodation_count
        ]):
            raise ValueError("Las cantidades de servicios no pueden ser negativas")
        if self.accommodation_payment_method == PaymentMethod.CARD and not self.accommodation_card_id:
            raise ValueError("Se debe especificar una tarjeta cuando el pago es con tarjeta")