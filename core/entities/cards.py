from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Card:
    card_number: str 
    card_pin: str 
    balance: float 
    id: Optional[int] = None
    is_active: bool = True
    


