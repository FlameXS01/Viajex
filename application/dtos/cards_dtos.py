from dataclasses import dataclass
from typing import Optional, List
from core.entities.card import Card  # ✅ Corregido import

@dataclass
class CreateCardRequest:
    card_number: str
    card_pin: str
    amount: float

@dataclass
class CreateCardResponse:
    success: bool
    card_id: int
    card_number: str
    amount: float
    is_active: bool
    message: Optional[str] = None

@dataclass
class GetCardRequest:
    card_id: Optional[int] = None
    card_number: Optional[str] = None

@dataclass
class GetCardResponse:
    success: bool
    card_id: int
    card_number: str
    card_pin: str
    amount: float
    is_active: bool
    message: Optional[str] = None

@dataclass
class UpdateCardRequest:
    card_id: int
    card_number: Optional[str] = None
    card_pin: Optional[str] = None
    is_active: Optional[bool] = None
    amount: Optional[float] = None

@dataclass
class UpdateCardResponse:  # ✅ Corregido nombre
    success: bool
    card_id: int
    card_number: str
    card_pin: str
    amount: float
    is_active: bool
    message: Optional[str] = None

@dataclass
class DeleteCardRequest:
    card_id: int  # ✅ Usar card_id consistente

@dataclass
class DeleteCardResponse:
    success: bool
    message: str

@dataclass
class ListCardsResponse:
    success: bool
    cards: List[GetCardResponse]  # ✅ Corregido "users" por "cards"
    count: int
    message: Optional[str] = None