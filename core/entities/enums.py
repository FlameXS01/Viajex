from enum import Enum

class DietStatus(Enum):
    """
    
    Enum que define los estados de una dieta
    
    """
    REQUESTED = "REQUESTED"
    LIQUIDATED = "LIQUIDATED"
    PARTIALLY_LIQUIDATED = "PARTIALLY_LIQUIDATED"

class PaymentMethod(Enum):
    """
    
    Enum que define los métodos de pago para alojamiento
    
    """
    CASH = "cash"
    CARD = "card"