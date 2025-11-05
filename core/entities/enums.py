from enum import Enum

class DietStatus(Enum):
    """
    
    Enum que define los estados de una dieta
    
    """
    REQUESTED = "requested"
    LIQUIDATED = "liquidated"
    PARTIALLY_LIQUIDATED = "partially_liquidated"

class PaymentMethod(Enum):
    """
    
    Enum que define los métodos de pago para alojamiento
    
    """
    CASH = "cash"
    CARD = "card"