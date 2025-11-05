from dataclasses import dataclass
from typing import Optional



@dataclass
class DietService:
    """

    Entidad de dominio DietService que representa los precios de servicios
    según localidad (local/no local).
    
    """
    is_local: bool
    breakfast_price: float
    lunch_price: float
    dinner_price: float
    accommodation_cash_price: float
    accommodation_card_price: float
    id: Optional[int] = None

    def __post_init__(self):
        """Validaciones después de la inicialización"""
        if self.breakfast_price < 0:
            raise ValueError("El precio del desayuno no puede ser negativo")
        if self.lunch_price < 0:
            raise ValueError("El precio del almuerzo no puede ser negativo")
        if self.dinner_price < 0:
            raise ValueError("El precio de la comida no puede ser negativo")
        if self.accommodation_cash_price < 0:
            raise ValueError("El precio de alojamiento en efectivo no puede ser negativo")
        if self.accommodation_card_price < 0:
            raise ValueError("El precio de alojamiento con tarjeta no puede ser negativo")