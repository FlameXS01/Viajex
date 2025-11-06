from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Card:
    id: Optional[int] = None
    card_number: str = ""
    card_pin: str = ""
    description: str = ""
    balance: float = 0.0
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()